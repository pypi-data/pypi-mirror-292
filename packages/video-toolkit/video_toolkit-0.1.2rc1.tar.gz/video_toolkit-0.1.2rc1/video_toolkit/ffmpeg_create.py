from pydub import AudioSegment
from typing import Union,List,Tuple, Literal, Callable, Dict
def export_audio(audio_segment:AudioSegment,
                 start_end_time_dict: Dict[int,Tuple[int,int]],
                 output_names:Dict[int,str],
                 output_folder:str = "",
                 progress_bar:bool = True,
                 ) -> None:
    
    # medium tested
    """
    Key feature: 
        1) Remove the invalid path in output_names automatically
    the timestamp should be in miliseconds units(for now)
    export multiple audio_segments
    make sure that index in output_names is also in start_end_time_dict
    
    example of start_end_time_dict
        start_end_time_dict = {
        6:  [14_633 , 15_933],
        7:  [24_455 , 25_534],
        8:  [25_700 , 27_550],
        9:  [27_899 , 30_000],
        10: [31_075 , 32_863],
        11: [33_439 , 36_188],
        12: [37_280 , 42_100],
        14: [42_865 , 47_224],
        
        }

    TOADD: replace => it would check if file already exists, if so depending on it's True or False, it would replace the file
    """
    import py_string_tool as pst
    clean_output_names = {}
    for inx, output_name in output_names.items():
        clean_output_names[inx] = pst.clean_filename(output_name)
    
    from tqdm import tqdm
    if progress_bar:
        loop_obj = tqdm(start_end_time_dict.items())
    else:
        loop_obj = start_end_time_dict.items()
    
    for inx, time_stamp in loop_obj:
        start_time, end_time = time_stamp
        try:
            output_name = clean_output_names[inx]
        except KeyError:
            raise KeyError(f"there's no index {inx} in your output_names(Dict). Please check your index again.")
        output_path = output_folder + "/" + output_name
        curr_audio = audio_segment[start_time:end_time]
        
        try:
            curr_audio.export(output_path)
        except PermissionError:
            raise KeyError(f"Please close the file {output_path} first.")