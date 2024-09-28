ONEHOTENCODER_VARS = ['model', 'motor_type','color','type']

TEMPORAL_VARS = ['year']

NUMERICALS_YEO_VARS = ["running", "motor_volume"]

QUAL_VARS = [
    'status']

qual_mappings = {'excellent': 3, 'good':2, 'crashed': 0, 'normal': 1, 'new': 4}

# the selected variables
FEATURES = [
    'year',
'running',
'status',
'motor_volume',
'model_hyundai',
'model_kia',
'model_mercedes-benz',
'model_nissan',
'model_toyota',
'motor_type_diesel',
'motor_type_gas',
'motor_type_hybrid',
'motor_type_petrol',
'motor_type_petrol and gas',
'color_beige',
'color_black',
'color_blue',
'color_brown',
'color_cherry',
'color_clove',
'color_golden',
'color_gray',
'color_green',
'color_orange',
'color_other',
'color_pink',
'color_purple',
'color_red',
'color_silver',
'color_skyblue',
'color_white',
'type_Coupe',
'type_Universal',
'type_hatchback',
'type_pickup',
'type_sedan',
'type_suv'
]