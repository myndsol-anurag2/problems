import numpy as np
import pytesseract
import cv2
from pdf2image import convert_from_path, convert_from_bytes
import re
from functools import cmp_to_key
import traceback
from difflib import SequenceMatcher as SM
import math
import copy

RESIZE_REQUIRED = False
FLOAT_REGEX = r'(?i)(?<![a-z.^$*+-?()[\]{}\|—/])(\d[\d,%.]+|\d)(?![a-z.^$*+-?()[\]{}\|—/])'
ACCEPTABLE_NON_ASCII_CHARS = ["₹"]
specialCharsToBreak = ["/", "'", ",", ":", ";", "\\", "-", ".", "(", ")", "[", "]", "{", "}", "<", ">", "?", "*"]
specialCharsToBreak.extend(ACCEPTABLE_NON_ASCII_CHARS)


# convert pytesseract's OCR result to google vision like response
def convert_tesseract_result(pytesseract_output):
    converted_output = []
    for ind, element in enumerate(pytesseract_output["level"]):
        # print(element)
        text = pytesseract_output["text"][ind]
        rectangle = [
            {"x": pytesseract_output["left"][ind], "y": pytesseract_output["top"][ind]},
            {"x": pytesseract_output["left"][ind] + pytesseract_output["width"][ind], "y": pytesseract_output["top"][ind]},
            {"x": pytesseract_output["left"][ind] + pytesseract_output["width"][ind], "y": pytesseract_output["top"][ind] + pytesseract_output["height"][ind]},
            {"x": pytesseract_output["left"][ind], "y": pytesseract_output["top"][ind] + pytesseract_output["height"][ind]}
            ]
        if text.replace(" ", "") != "" :
            new_element = {"description": text, "boundingPoly": {"vertices": rectangle}}
            # print(new_element)
            converted_output.append(new_element)
    return converted_output

# getting OCR result using pytesseract for an image
def get_tesseract_response(cv2_image=None, preprocess=RESIZE_REQUIRED, min_img_side=1080, max_img_side=1920):
    if preprocess:
        cv2_image, _ = resize_image(cv2_image, min_side=min_img_side, max_side=max_img_side)

    # image_text = pytesseract.image_to_string(cv2_image)
    pytess_ocr = pytesseract.image_to_data(cv2_image, output_type=pytesseract.Output.DICT)
    # print(pytess_ocr)
    vertices = convert_tesseract_result(pytess_ocr)
    verticeArray = [[vertice["description"], vertice["boundingPoly"]["vertices"]] for vertice in vertices]
    OCRParams = {
        "documentOCR": get_full_string(verticeArray=verticeArray),
        "vertices": vertices
    }
    verts = createDictOfVertices(
            OCRParams['vertices'])
    OCRParams['verts'] = verts
    print("OCRParams", OCRParams)
    return OCRParams

def createDictOfVertices(vertices, englishOnly=True, splitBySpecialChar=True, unicode_status=False):
    """
    Create a dict of all "words" and their occurences returned as a
     response from Tesseract response.
    """

    global specialCharsToBreak
    global ACCEPTABLE_NON_ASCII_CHARS

    # dict to be populated
    verts = {}
    unicode_char_flag = False
    unicode_count = 0
    # Iterating JSON response
    for vertice in vertices:
        try:
            try:
                if (englishOnly):
                    vertice['description'] = vertice['description'].encode("ascii").decode("ascii")
            except UnicodeEncodeError:
                # Raise error on non Roman characters if not needed
                new_vertice_description = ""
                for character in vertice['description']:
                    if character in ACCEPTABLE_NON_ASCII_CHARS:
                        new_vertice_description += character  # add as-is
                    else:
                        new_vertice_description += character.encode("ascii").decode("ascii")                            
                vertice["description"] = new_vertice_description
            # Flag to indicate if the vertices weren't returned properly.
            faultyVertices = False 
            for coordinate in vertice['boundingPoly']['vertices']:
                # Faulty response
                if 'x' not in coordinate or 'y' not in coordinate:
                    faultyVertices = True
            # Continue iteration and don't append anything if faulty vertice
            if faultyVertices or vertice['description'] == '' or len(vertice['boundingPoly']['vertices']) != 4:
                print("skipping vertices", vertice['description'])
                continue
            if vertice['description'] in verts:
                verts[vertice['description']].append(vertice['boundingPoly']['vertices'])
            else:
                if splitBySpecialChar:
                    split_vertices = splitVerticeBySpecialChar(vertice)
                    for i in split_vertices:
                        if i['description'] == '':
                            continue
                        if i['description'] in verts:
                            verts[i['description']].append(i['boundingPoly']['vertices'])
                        else:
                            verts[i['description']] = [i['boundingPoly']['vertices']]
                else:
                    verts[vertice['description']] = [vertice['boundingPoly']['vertices']]
        # Raised when englishOnly is True and non-ascii encountered
        except UnicodeEncodeError:
            unicode_count = unicode_count + 1
    if unicode_status:
        if(unicode_count > 10):
            unicode_char_flag = True
        return verts, unicode_char_flag
    return verts

# Recursive by default; splits by multiple special char occurences
def splitVerticeBySpecialChar(vertice, recursive=True, specialCharsToBreak=specialCharsToBreak, rec=0):
    try:
        verticeText = vertice['description']
        verticeBox = vertice['boundingPoly']['vertices']
        horizontalSpanPerCharacter = (verticeBox[2]['x'] - verticeBox[0]['x']) / len(verticeText)
        topY = verticeBox[0]['y']
        botY = verticeBox[2]['y']
    # Empty string in vertice description
    except ZeroDivisionError:
        return [vertice]

    splitVerticesArray = []
    specialCharPresent = False
    for index, character in enumerate(verticeText):
        if character not in specialCharsToBreak:
            continue
        else:
            # This vertice needs to be processed
            specialCharPresent = True
            specialCharIndex = index
            specialChar = character
            break # Further special character breaks will be handled by recursion

    if specialCharPresent is True:
        # Before the special char polygon
        temp_vertice = {}
        temp_vertice['description'] = verticeText[:specialCharIndex]
        temp_vertice['boundingPoly'] = {}
        temp_vertice['boundingPoly']['vertices'] = []
        temp_vertice_x_left = verticeBox[0]['x']
        temp_vertice_x_right = temp_vertice_x_left + (specialCharIndex * horizontalSpanPerCharacter)
        temp_vertice['boundingPoly']['vertices'] = [{'x': int(temp_vertice_x_left), 'y': topY}, {'x': int(temp_vertice_x_right), 'y': topY}, 
                                                    {'x': int(temp_vertice_x_right), 'y': botY}, {'x': int(temp_vertice_x_left), 'y': botY}]
        splitVerticesArray.append(temp_vertice)

        # Special char polygon
        item_vertice = {}
        item_vertice['description'] = specialChar
        item_vertice['boundingPoly'] = {}
        item_vertice['boundingPoly']['vertices'] = []
        item_vertice_x_left = temp_vertice_x_right
        # len(character) is always gonna be 1
        item_vertice_x_right = item_vertice_x_left + horizontalSpanPerCharacter
        item_vertice['boundingPoly']['vertices'] = [{'x': int(item_vertice_x_left), 'y': topY}, {'x': int(item_vertice_x_right), 'y': topY}, 
                                                    {'x': int(item_vertice_x_right), 'y': botY}, {'x': int(item_vertice_x_left), 'y': botY}]
        splitVerticesArray.append(item_vertice)

        # After the special char polyon
        if index < len(verticeText) - 1:
            remaining_vertice = {}
            remaining_vertice['description'] = verticeText[specialCharIndex+1:]
            remaining_vertice['boundingPoly'] = {}
            remaining_vertice['boundingPoly']['vertices'] = []
            remaining_vertice_x_left = item_vertice_x_right
            # len(item) is "almost" always gonna be 1
            remaining_vertice_x_right = verticeBox[2]['x']
            remaining_vertice['boundingPoly']['vertices'] = [{'x': remaining_vertice_x_left, 'y': topY}, {'x': remaining_vertice_x_right, 'y': topY}, 
                                                             {'x': remaining_vertice_x_right, 'y': botY}, {'x': remaining_vertice_x_left, 'y': botY}]
            if recursive:
                remaining_vertice_split = splitVerticeBySpecialChar(remaining_vertice, recursive=True, specialCharsToBreak=specialCharsToBreak, rec=rec)
                splitVerticesArray.extend(remaining_vertice_split)
            else:
                splitVerticesArray.append(remaining_vertice)
    # No special characters present
    else:
        splitVerticesArray = [vertice]

    return splitVerticesArray

def get_full_string(verticeArray, noSpaceChars='', noSpaceBeforeChars='', noSpaceAfterChars=''):
	""" 
	Stitch strings from array of verts to make a phrase or sentence. This 
	returns a singular string.

	:param dict verticeArray: [refer documentation]
	:param string noSpaceChars: all characters that have to be appended without 
		a space like "/" or "-"
	:param string noSpaceAfterChars: all characters that have to be appended 
		without a space like "'" after them
	:param string noSpaceBeforeChars: all characters that have to be appended 
		without a space like ":" before them
	:returns: string; stitched from all verts passed
	"""
	if len(verticeArray) == 0:
		return ""
		
	# Intialize 'return text' with the text of the first vert passed
	returnText = verticeArray[0][0]

	# Iterate verts from index 1 (0 already included while assignment) [note use of i + 1 instead of i]
	for i in range(len(verticeArray) - 1):
		# Append with space if verts on same line
		if same_line(verticeArray[i][1], verticeArray[i + 1][1]):
			# Append without spaces if special characters that don't warrant a space between encountered
			if verticeArray[i + 1][0] in noSpaceChars or verticeArray[i][0] in noSpaceChars:
				returnText += verticeArray[i + 1][0]
			elif verticeArray[i][0] in noSpaceAfterChars:
				returnText += verticeArray[i + 1][0]
			elif verticeArray[i + 1][0] in noSpaceBeforeChars:
				returnText += verticeArray[i + 1][0]
			# Append with space 'normally'
			else:
				returnText += " " + verticeArray[i + 1][0]
		# Append with new line if vert present on a different line than the previous
		else:
			returnText += "\n" + verticeArray[i + 1][0]

	return returnText

def same_line(a, b, width=None):
	""" 
	This function checks if a box (or an area) is 'on the same line' of 
	another box. This will return true if one box's height completely 
	encompasses the other OR the boxes are present on the 'same' line 
	with misalignment threshold that defaults to half the height of shorter 
	box. This threshold can also be provided as an argument to the function 
	but giving a value greater than half of the (passed) boundingPolygon's 
	height may (and most probably will) cause misclassifications; also 
	giving a value like 0 may also produce artefacting in documents with 
	special characters or with tilt.

	PARAMETERS
	----------
	a, b - boundingPolygons -> that have to be classified
	width - integer -> threshold for misalignment

	RETURNS
	-------
	aboolean -> 'sameline-ness' of the two boxes
	"""
	# Return True if a vert is None
	if not a or not b:
		return True
	# Defaulting width threshold to half of height of shorter boundingPolygon
	if width is None:
		aHeight = abs(a[0]['y'] - a[2]['y'])
		bHeight = abs(b[0]['y'] - b[2]['y'])
		width = min(aHeight, bHeight) / 2
	try:
		# If vert b's "height" completely encompasses vert a's "height" 
		if a[0]['y'] > b[0]['y'] and a[2]['y'] < b[2]['y']:
			return True
		# If vert a's "height" completely encompasses vert b's "height"
		elif b[0]['y'] > a[0]['y'] and b[2]['y'] < a[2]['y']:
			return True
		# If same line withtin the threshold
		elif a[0]['y'] < b[0]['y']+ width and a[0]['y'] > b[0]['y'] - width:
			return True
		else:
			return False
	except:
		return False


def compute_resize_scale(image_shape, min_side=400, max_side=600, upscale=False):
	
    (h, w, _) = image_shape

    # Image is bigger than max_side 
    if (min(h, w) > min_side and max(h, w) > max_side) or upscale:
        smaller_side = min(h, w)
        scale = min_side / smaller_side  # smaller side will be = min_side
        larger_side = max(h, w)
        if larger_side * scale > max_side:
            scale = max_side / larger_side # larger side will be = max_side

    # Image is smaller and upscaling is not allowed
    else:
        scale = 1

    return scale


# Downscale images
def resize_image(img, min_side=400, max_side=600, upscale=False):
	""" 
	Resize an image such that the size is constrained to min_side and max_side.
	"""

	# compute scale to resize the image
	scale = compute_resize_scale(img.shape, min_side=min_side, max_side=max_side, upscale=upscale)
	# resize the image with the computed scale
	img = cv2.resize(img, None, fx=scale, fy=scale)
	return img, scale


def extract_table_data(tess_response):
    table_created = []
    floats_found = float_collector(tess_response)
    print(floats_found)
    top_line = get_top_line(tess_response["vertices"], default_y_ratio=0)
    bottom_line = get_bottom_line(tess_response["vertices"], 0)
    print(top_line)
    print(bottom_line) 
    filtered_floats = []
    for float_found in floats_found:
        if float_found[1][2]["y"] > top_line and float_found[1][0]["y"] < bottom_line:
            filtered_floats.append(float_found)
    print("filtered_floats", filtered_floats)
    column_wise_floats = create_column_cluster(filtered_floats)
    print("column_wise_floats",column_wise_floats)
    page_table_created = create_row_cluster(column_wise_floats)
    
    print("page_table_created", page_table_created)
    table_created.append(page_table_created)
    return table_created
    
def create_column_cluster(filtered_floats, casenumber=None):
    """
    [1234, [{}{}{}{}]]
    [[1234, [{}{}{}{}]], [1234, [{}{}{}{}]], [1234, [{}{}{}{}]], [1234, [{}{}{}{}]], [1234, [{}{}{}{}]]]

    Sample Output (visualization):
    [
        [1234, 1234, 8765, 1234],
        [5364, 4564, 3452, 2345],
        [3453, 2345],
        [0000, 1234, 4566],
    ]
    Interpretation:
    total columns: 4; columns have 4, 4, 2, 3 elements respectively
    """

    global CASE_SUBMODULE

    column_wise_floats = []

    for filtered_float in filtered_floats:
        column_found = False
        for ind, possible_column in enumerate(column_wise_floats):
            # Float belongs to an existing column
            if sameCol(filtered_float[1], possible_column[0][1]):
                column_wise_floats[ind].append(filtered_float)
                column_found = True
        # Define new column
        if not column_found:
            column_wise_floats.append([filtered_float])
    sorted_column_wise_floats = []
    for unsorted_column in column_wise_floats:
        sorted_column = sorted(unsorted_column, key=lambda i: i[1][0]["y"])
        sorted_column_wise_floats.append(sorted_column)
    
    # filtering columns having multiple values lying in the same box(ex: float collector giving 2 floats i.e. [9898, 9] for the value 9,898 in the invoice)
    final_columns = []

    for column in sorted_column_wise_floats:
        checked_values = [] # new column with no overlapping values
        for i, val_i in enumerate(column):
            overlap_value = None
            for j, val_j in enumerate(column):
                if i == j:
                    continue
                # Our value is present inside some other value
                if inside(val_j[1], val_i[1]):
                    overlap_value = val_j
                    break
            
            # This value is unique
            if overlap_value is None:
                checked_values.append(val_i)
        final_columns.append(checked_values)          

    return final_columns

def create_row_cluster(column_wise_floats, casenumber=None):
    """
    Sample Output:
    [
        [1234, 1234, 8765, 1234],
        [5364, 4564, 3452, 2345],
        [3453, null, null, 2345],
        [0000, null, 1234, 4566],
    ]
    Interpretation:
    total columns: 4; all columns have 4 elements (rows)

    It is necessary that the floats have been sorted by positions
     for the (efficient) algorithm to work
    """

    global CASE_SUBMODULE

    result = []

    x_bounds_collection = []
    for column in column_wise_floats:
        x_min = float("inf")
        x_max = float("-inf")
        for value in column:
            if value is not None:
                x_min = min(value[1][0]["x"], x_min)
                x_max = max(value[1][2]["x"], x_max)
        x_bounds_collection.append((x_min, x_max))

    # Iterating "reference" column
    for col_i_ind in range(len(column_wise_floats)):

        column_i = column_wise_floats[col_i_ind]

        # All values have been popped
        if column_i == []:
            continue
        
        while column_i != []:

            value_i = column_i.pop(0)
            
            # Each row will have a value for each column
                # row element is of the data structure: [(float) value, box/position]
            row_elements = [[None, None]] * len(column_wise_floats)
            row_elements[col_i_ind] = value_i
            
            # Iterating "secondary" column
            for col_j_ind in range(len(column_wise_floats)):
                
                column_j = column_wise_floats[col_j_ind]

                sameLine_value_found = False
                if col_j_ind == col_i_ind:
                    continue

                pop_indices = []  # note indices to pop after iteration is completed
                for value_j_ind in range(len(column_j)):
                    
                    value_j = column_j[value_j_ind]

                    # secondary column has a value in line with primary's value
                    if same_line(value_i[1], value_j[1]):
                        row_elements[col_j_ind] = value_j
                        pop_indices.append(value_j_ind)
                        sameLine_value_found = True
                        
                for i in pop_indices[::-1]:
                    column_j.pop(i)

                # No value found in sameLine for this column
                if sameLine_value_found is False:
                    dummy_cell = copy.deepcopy(value_i[1])
                    dummy_cell[0]['x'] = dummy_cell[3]['x'] = x_bounds_collection[col_j_ind][0]
                    dummy_cell[1]['x'] = dummy_cell[2]['x'] = x_bounds_collection[col_j_ind][1]
                    row_elements[col_j_ind] = [None, dummy_cell]
                # desc = get_description_from_zone(dummy_cell, row_elements, cv2_image)
                
            result.append(row_elements)

    sorted_result = []
    # Sort every element in row by their x coordinates 
    for row in result:
        sorted_row_element = sorted(row, key=lambda i:i[1][0]["x"])
        sorted_result.append(sorted_row_element)
    
    return sorted_result

def sameCol(a, b):
	""" 
	This function checks if two polygons are "vertically aligned" or not. 
	It will return True if one of the polygons completely encompasses 
	the other or if the horizontal (width) overlap between the two polygons 
	is greater than the width of first polygon not in overlap. [First 
	polygon is the polygon with lesser abscissa value]

	PARAMETERS
	----------
	a, b - array of (four) coordinates

	RETURNS
	-------
	a boolean representing the 'same-column-ness' of the vert a and b

	"""
	if a[0]['x'] <= b[0]['x'] and a[1]['x'] >= b[1]['x']:
		return True
	if a[0]['x'] >= b[0]['x'] and a[1]['x'] <= b[1]['x']:
		return True
	if a[0]['x'] >= b[0]['x'] and a[0]['x'] <= b[1]['x']:
		if b[1]['x'] - a[0]['x'] >= a[0]['x'] - b[0]['x']:
			return True
		return False
	if b[0]['x'] >= a[0]['x'] and b[0]['x'] <= a[1]['x']:
		if a[1]['x'] - b[0]['x'] >= b[0]['x'] - a[0]['x']:
			return True
		return False
	else:
		return False

def inside(outer, inner, threshold=None):
	""" 
	This function checks if a box (or an area) is 'inside' another box.

	PARAMETERS
	----------
	outer, inner - boundingPolygon
	threshold - integer -> threshold of overflow after which the function 
		changes its classification

	RETURNS
	-------
	a boolean representing 'inside-ness' the inner box 
	"""
	# Return True if a vert is None
	if not inner or not outer:
		return True
	# Default threshold is zero
	if threshold is None:
		threshold = 0.3 * min(outer[2]['x']-outer[0]['x'], inner[2]['x']-inner[0]['x'])
	outer_h_center = (outer[2]["x"] + outer[0]["x"]) // 2
	outer_v_center = (outer[2]["y"] + outer[0]["y"]) // 2
	outer_center = {"x": outer_h_center, "y": outer_v_center}
	inner_h_center = (inner[2]["x"] + inner[0]["x"]) // 2
	inner_v_center = (inner[2]["y"] + inner[0]["y"]) // 2
	inner_center = {"x": inner_h_center, "y": inner_v_center}
	if pixelInside(outer_center, inner) or pixelInside(inner_center, outer):
		if getBoxArea(outer) >= getBoxArea(inner):
			return True
		else:
			return False
	else:
		return False

def getBoxArea(box):
    length = abs(box[0]['x'] - box[1]['x'])
    breadth = abs(box[0]['y'] - box[3]['y'])
    return length * breadth

def pixelInside(pixel, box):
	if (pixel['x'] > box[0]['x']) and (pixel['x'] < box[2]['x']):
		if (pixel['y'] > box[0]['y']) and (pixel['y'] < box[2]['y']):
			return True
	return False
    
def get_top_line(vertices, default_y_ratio=0.33):
    """
    getting top line from the google api response for an invoice

    Parameters
    ----------
    gApiResponse : list
        list of words along with their coordinates
        in the format returned by google vision API
    Returns
    -------
    y_min : int
        returns y-coordinate of the headers line
    """
    
    FIRST_CUTOFF_ROW_CONSTS = [
        'description', 'desc', 'goods', 'article', 'articles', 'product', 'service', 'products', 'services', 
        'hsn/sac', 'hsn', 'sac', 'code', 'qty', 'quantity', 'rate', 'unit', 'unit', 'per', 'uom', 'measurement', 
        'cgst', 'sgst', 'igst', 'gst', 'tax', 'taxes', 'amount', 'total', 'taxes','taxable', 'value', 
        'serial', 'sno', 'si', 'srno', 'particulars'
        ]
    
    useful_words = []
    
    max_y = 900
    for i in range(10):
        try:
            max_y = vertices[-1*i]['boundingPoly']['vertices'][2]['y']
            break
        except:
            continue

    for bounding_box in vertices:
        if 'boundingPoly' not in bounding_box.keys():
            continue
        word, boundingPoly = bounding_box['description'], bounding_box['boundingPoly']
        for check_word in FIRST_CUTOFF_ROW_CONSTS:
            if(check_word.lower() in word.lower()):
                useful_words.append(bounding_box)
    print("useful_words", useful_words)
    lines = get_words_nearby(useful_words)
    print("lines", lines)
    max_len_index = 0
    min_y = math.inf
    for index, line in enumerate(lines):
        if(len(line) >= 3):
                if line[0]['boundingPoly']['vertices'][0]['y'] < min_y:
                    min_y = line[0]['boundingPoly']['vertices'][0]['y']  
                    max_len_index = index
                    
    if lines:           
        useful_line = lines[max_len_index]
        y_min = math.inf
        for bounding_box in useful_line:
            p1, _, _, _ = bounding_box['boundingPoly']['vertices']
            if (p1['y'] < y_min):
                y_min = p1['y']
    else:
        y_min = max_y * default_y_ratio
        
    return y_min

def get_bottom_line(vertices, top_line):
    """
    getting bottom line from the google api response for an invoice

    Parameters
    ----------
    gApiResponse : list
        list of words along with their coordinates
        in the format returned by google vision API
    top_line: int
        y-coordinate of the topline
        this func will only give lines that are below this line
    Returns
    -------
    y_min : int
        returns y-coordinate of the headers line
    """

    MAX_LEN_LINE = 4
    CUTOFF_ROW_CONSTS = ['total']
    
    useful_vertices = []

    for vertice in vertices:
        if "boundingPoly" not in vertice.keys():
            continue
        word, boundingPoly = vertice['description'], vertice['boundingPoly']
        for check_word in CUTOFF_ROW_CONSTS:
            if(check_word.lower() == word.lower()):
                useful_vertices.append(vertice)
                
    y_min = math.inf

    for vertice in useful_vertices:
        _, _, _, p4 = vertice['boundingPoly']['vertices']
        if (p4['y'] < y_min) and (p4['y'] > top_line + 100):
            y_min = p4['y']
    
    
    return y_min

def get_words_nearby(words_list, proximity_range=25):
    """ 
    Get words which are in same line
    line height is defined by the proximity range in pixels.
    
    Parameters
    ----------
    words_list : list
        list of words along with their coordinates
        in the format returned by google vision API
    proximity_range : int
        proximity in which if the words fall they will
        be taken as to be in the same line
    Returns
    -------
    lines : list
        returns list of lists ( lines )
    """
    
    lines = []

    for index, bounding_box in enumerate(words_list):
        unique_words_list = [] # list so that words dont repeat
        line = []
        word = bounding_box['description']
        unique_words_list.append(word.strip().lower())
        point1, _, _, _ = bounding_box['boundingPoly']['vertices']
        y_min = point1['y']
        
        #   Copying word_list as need to iterate over it again
        word_list_copy = words_list[:]
        #   removing the index used for this word
        del word_list_copy[index]
        
        for next_bounding_box in word_list_copy:
            word, next_boundingPoly = next_bounding_box['description'], next_bounding_box['boundingPoly']['vertices']
            next_point1, _, _, _ = next_boundingPoly
            next_y_min = next_point1['y']
            
            if(abs(y_min - next_y_min) < proximity_range) and (word.strip().lower() not in unique_words_list):
                line.append(next_bounding_box)
                unique_words_list.append(word.strip().lower())
        
        if(len(line)):
            line.insert(0, bounding_box)
            lines.append(line)
    
    return lines
    

# Collects floats from a document using regex only
def float_collector(OCRParams, float_regexes=[FLOAT_REGEX], casenumber = None):

    regex_matches = []
    
    for possible_regex in float_regexes:
        matches = re.findall(possible_regex, OCRParams["documentOCR"])
        matches = list(set(matches))
        clean_matches = [match.replace(" ", "").replace(",", "").replace("%", "") for match in matches]
        for match, clean_match in zip(matches, clean_matches):
            try:
                value = float(clean_match)
                if value == 0:
                    continue
                getBoxable_string = re.sub(r"[ ]*,[ ]*", r" , ", match)
                getBoxable_string = re.sub(r"[ ]*\.[ ]*", r" . ", getBoxable_string)
                occurences = getBox(getBoxable_string, OCRParams["verts"], matchingThreshold=1)
                if value > 50 and len(occurences) == 0:
                    getBoxable_string = re.sub(r"[ ]*\.[ ]*.*", "", getBoxable_string)
                    occurences.extend(getBox(getBoxable_string, OCRParams["verts"], matchingThreshold=1))
                regex_matches.extend([(value, occurence) for occurence in occurences])
            except Exception as e:
                traceback.print_exc()
                continue
    distinct_regex_matches = []
    for regex_match in regex_matches:
        if regex_match not in distinct_regex_matches and regex_match != []:
            distinct_regex_matches.append(regex_match)
    return regex_matches

def getBox(phrase, verts, matchingThreshold=0.9, sameLine=True, occurence=0, sortedVertsPassed=False):

	# Track number of 'complete matches of the phrase' have been encountered; this isn't used if occurence=0.
	boxesMatched = 0
	# If dict of verts passed
	if type(verts) == dict or not sortedVertsPassed:
		# Sort the verts passed
		sortedVerts = getSortedVerticeArray(verts)
	# If already sorted vert [text, [occurences]] passed
	else:
		sortedVerts = sortedVerts
	# Number of words in document
	documentLength = len(sortedVerts)
	# Get all words in the phrase
	words = phrase.split(' ')
	# Number of words in the phrase
	phraseLength = len(words)
	vss = []
	bounds = []
	# String used for building a phrase from the document equal to the length of the phrase passed
	#  This will then be matched with the phrase passed. If it matches then the box will be returned
	builtPhrase = ''
	builtPhraseVerts = []
	# Index variable for iterating document
	i = 0
	# Index for building phrase of a length equal to the length of phrase passed
	j = 0
	
	# Iterate sorted verts
	for i in range(documentLength - phraseLength +1):	
		# Reset phrase building
		builtPhrase = ''
		builtPhraseVerts = []
		j = 0
		# Building a word of the length of the phrase
		for j in range(phraseLength):
			builtPhrase = builtPhrase + sortedVerts[i + j][0]
			builtPhraseVerts.append(sortedVerts[i + j][1])
			builtPhrase = builtPhrase + ' '
		builtPhrase = builtPhrase.strip()
		# Phrase matched!!
		if (SM(None, phrase.lower(), builtPhrase.lower()).ratio() >= matchingThreshold):
			boxesMatched = boxesMatched + 1
			# Pay heed to this box only if <all> or <this specific> occurence(s) were/was requested 
			if((occurence == 0) or (boxesMatched == occurence)):
				bounds.append(getBound(builtPhraseVerts))
				# No need to continue if specific occurence needed and found
				if((occurence > 0) and (boxesMatched == occurence)):
					break
			# Continue to find further occurences if this wasn't needed
			else:
				continue
		# Phrase did not match
		else:
			builtPhrase = ''
			builtPhraseVerts = []
			continue
	return bounds

def getSortedVerticeArray(verts):
	""" 
	Generate verticeArray from the conventional strucutre of 'verts'. This will always pass through sortXY and then return
	the verticeArray
	PARAMETERS
	----------
	verts

	RETURNS
	-------
	An array of subarrays; each subarray contains the text of the vert in the 0th index, the coordinates in the second
	"""
	verticeArray = []
	# Create a array that can be sorted
	for i in verts:
		for vert in verts[i]:
			verticeArray.append([i, vert, 0])
	return sortXY(verticeArray)

def sortXY(verticeArray, ignoreHorizontal=False, ignoreVertical=False):
	""" 
	This function sorts the verts according the readable format (left to right; top to bottom). 
	It can also sort just on the x or y coordinate
	PARAMETERS
	----------
	verticeArray - verticeArray
	ignoreHorizontal - Boolean; Pass True for sorting on just y
	ignoreVertical - Boolean; Pass True for sorting on just x

	RETURNS
	-------
	verticeArray sorted in the same structure in which it was passed. (uses sorted with n(log(n)) as worst case)

	NOTE: Important edge case


							|	Some other	|
	|					|	|	Text here	|
	|	Some Text Here	|
	|					|	|	Yet some	|
							|	other text	|

	If document has words printed like the 'diagram' above then 'Some other Text here' can be ordered first, 
	then 'Some Text Here', and then 'Yet some other text' even if readability dicatates 'Some Text Here' to 
	be before 'Some other Text here'.
	"""
	if ignoreHorizontal is False and ignoreVertical is False:
		# Sorting will be done top to bottom, left to right; see comparator
		verticeArray = 	sorted(verticeArray, key=cmp_to_key(vertCompare))
	elif ignoreHorizontal is True:
		# Sorting will be done top to bottom
		verticeArray = 	sorted(verticeArray, key=cmp_to_key(below))
	elif ignoreVertical is True:
		# Sorting will be done left to right
		verticeArray = 	sorted(verticeArray, key=cmp_to_key(right))

	return verticeArray

def vertCompare(a, b):
	""" 
	A comparator function that checks the order of two vertices in the 
	english (readable) format; to check precedence it uses the functions 
	below and right. 

	PARAMETERS
	----------
	a, b - boundingPolygons

	RETURNS
	-------
	An integer 
	
	This comparator follows the convention, taking two 
	arguments and returning -1 if the first succeeds the second and 
	1 if the first preceeds the second. This function does not return 
	0 value assuming that two verts will never actually the *same*.

	"""
	if below(a[1], b[1]):
		return 1
	elif below(b[1], a[1]):
		return -1
	elif not same_line(a[1], b[1]):
		if a[1][0]["y"] < b[1][0]["y"]:
			return 1
		else:
			return -1
	else:
		if right(a[1], b[1]):
			return 1
		else:
			return -1

def right(right_box, left_box, threshold=None):
	""" 
	This function checks if a box (or an area) is 'on the right' of another 
	box (within) a horizontal threshold of overlap. This overlap threshold 
	defaults to half width of 'narrower' box. This threshold can also be 
	provided as an argument to the function but giving a value greater 
	than half of the (passed) boundingPolygon's width may (and most probably 
	will) cause misclassifications.

	PARAMETERS
	----------
	right, left - boundingPolygon -> that have to be classified
	width - integer -> threshold for misalignment

	RETURNS
	-------
	boolean -> if the right arg is to the "right" of the left arg
	"""
	# Return True if a vert is None
	if not left_box or not right_box:
		return True
	# Default threshold; 20% of width of narrower polygon
	if threshold is None:
		threshold = 0.2 * min(right_box[2]['x'] - right_box[0]['x'], left_box[2]['x'] - left_box[0]['x'])
	# Check left boundary of right box with right boundary of left word 
	if (right_box[0]['x'] + threshold >= left_box[2]['x']):
		return True
	# Default to False 
	else:
		return False

# 1.3 Below
def below(bottom_box, top_box, include=False, ignoreHorizontal=False, threshold=None):
	""" 
	This function checks if a box (or an area) is 'below' another box 
	within a vertical overlap threshold.

	PARAMETERS
	----------
	bottom_box, top_box - boundingPolygon -> that have to be classified
	include - boolean that dictates whether the bottom_box vertice can 
		occur on the sameLine as top
	ignoreHorizontal - boolean that dictates whether horizontal position 
		has to be compared or not
	threshold - threshold of overlap allowed after which the function 
		changes the return boolean

	RETURNS
	-------
	boolean -> the 'below-ness' of the bottom_box vert compared to the top
	"""
	# Return True if one value absent
	if not bottom_box or not top_box:
		return True
	# Deafult threshold is 20% the height of the shorter box
	if threshold is None:
		threshold = 0.45 * min((top_box[2]['y'] - top_box[0]['y']), (bottom_box[2]['y'] - bottom_box[0]['y']))
	try:
		# If a non-negative threshold not provided [default]
		if not include:
			if bottom_box[0]['y'] > top_box[2]['y'] - threshold:
				return True
			else:
				return False
		else:
			# True bottom
			if bottom_box[0]['y'] > top_box[2]['y'] - threshold:
				return True
			# SameLine
			elif same_line(bottom_box, top_box):
				if ignoreHorizontal is True and include is True:
					return True
				else:
					if right(bottom_box, top_box):
						return True
					else:
						return False
			else:
				return False
	except:
		traceback.print_exc()
		return False

def getBound(boundingPolygons):
	"""
	This function gives a bounding polygon (array of 4 coordinates) that encompaasses all the polygons passed.
	PARAMETERS
	----------
	boundingPolygons - An array of boundingPolygon(s)

	RETURNS
	-------
	An array with (four) coordinates
	"""
	# Boolean for setting max value (once) while iterating the polygons.
	updateIntialized = False
	xmax = xmin = ymax = ymin = 0
	# Update max variables to get a bounding polygon that encompasses all the areas passed
	for polygon in boundingPolygons:
		for vert in polygon:
			# Set the max variables directly the first time
			if(not updateIntialized):
				xmax = vert['x']
				xmin = vert['x']
				ymax = vert['y']
				ymin = vert['y']
				# switch to else block after first update
				updateIntialized = True
			else:
				xmax = max(vert['x'], xmax)
				xmin = min(vert['x'], xmin)
				ymax = max(vert['y'], ymax)
				ymin = min(vert['y'], ymin)
	return [{'x': xmin, 'y': ymin}, {'x': xmax,'y': ymin}, {'x': xmax,'y': ymax}, {'x': xmin,'y': ymax}]




if __name__ == "__main__":
    filepath = "test.pdf"
    images = convert_from_path(filepath)
    height, width = images[0].size
    print(height)
    tess_response = get_tesseract_response(cv2_image=images[0])
    print(tess_response)
    result = extract_table_data(tess_response)
    # print(tess_response)
    # tess_OCR = pytesseract.image_to_string(images[0])
    # print(tess_response)
    # print(tess_OCR)