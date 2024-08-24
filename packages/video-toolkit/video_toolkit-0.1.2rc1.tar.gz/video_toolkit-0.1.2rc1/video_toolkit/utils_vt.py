# imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 06_ffmpeg\ffmpeg_01.py"
from typing import Union,List,Tuple, Literal, Callable, Dict
from pathlib import Path
import sys
import datetime
import python_wizard as pw
import os_toolkit as ost
import dataframe_short as ds
import pkg_resources

import pandas as pd
import seaborn as sns
from pydub import AudioSegment
alarm_done_path = pkg_resources.resource_filename(__name__, 'assets/Sound Effect positive-logo-opener.wav')
sound_error_path = pkg_resources.resource_filename(__name__, 'assets/Sound Effect Error.wav')

CODEC_DICT = {'.mp3': "libmp3lame",
                  'mp3' : "libmp3lame",
                  '.wav': "pcm_s24le",
                  'wav' : "pcm_s24le"
                  }

# v02 => add extract_audio2, extract_subtitle, _extract_media_setup,extract_sub_1_video
# get_metadata2, get_all_metadata, get_metadata
# get_subtitle_index,get_audio_index,get_video_index,_get_media_index,get_subtitle_extension,
# get_audio_extension,get_video_extension, _get_media_extension


def text_to_milisecond(time_text:Union[str,int,float],delimiter:str = ".") -> Union[int,float]:
    """
    time_text should be seperated by dot for :
    convert strings to miliseconds to easily convert back and forth between video view and pydub input
    if it's already int it would return the same
    
    Convert time text to milliseconds.

    Args:
    time_text (Union[str, int, float]): Time in format "hr.min.sec" or "min.sec" or milliseconds.

    Returns:
    Union[int, float]: Time in milliseconds.

    Examples:
    "4.32" => (4*60 + 32) * 1000 = 272000 ms (4 min 32 sec)
    "1.40.32" => (1*3600 + 40*60 + 32) * 1000 = 6032000 ms (1 hr 40 min 32 sec)
    """
    if isinstance(time_text, (int, float)):
        return time_text

    if not isinstance(time_text, str):
        raise ValueError("Input must be a string, int, or float.")

    parts = time_text.split(delimiter)
    
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return (minutes * 60 + seconds) * 1000
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return (hours * 3600 + minutes * 60 + seconds) * 1000
    else:
        raise ValueError("Invalid time format. Use 'min.sec' or 'hr.min.sec'.")

def clean_subtitle(string:str):
    import re
    pattern1 = "<.*?>"
    
    pattern2 = "<\/[a-zA-Z]>"
    
    string1 = re.sub(pattern1, "", string)
    string2 = string1.replace("\n"," ")
    new_string = re.sub(pattern2,"",string2)
    return new_string

def audio_duration(video_path):
    from pydub import AudioSegment
    from datetime import datetime, timedelta

    if isinstance(video_path,str):
        video_audio = AudioSegment.from_file(video_path)
    else:
        video_audio = video_path

    # Get the duration of the audio segment in milliseconds
    duration_ms = len(video_audio)

    # Convert the duration from milliseconds to a timedelta object
    duration = timedelta(milliseconds=duration_ms)

    # Create a dummy datetime object with a zero timestamp
    dummy_datetime = datetime(1, 1, 1, 0, 0, 0)

    # Add the duration to the dummy datetime to get the final datetime
    final_datetime = dummy_datetime + duration

    return final_datetime.time()

# Sub

def split_1audio_by_subtitle(
    video_path: Union[str,Path],
    subtitle_path,
    output_folder,
    prefix_name = None,
    out_audio_ext = "wav",
    alarm_done:bool = False,
    verbose:int = 1,
    include_sentence:bool = True
        ) -> None:
    import time
    import os
    from pydub import AudioSegment
    from playsound import playsound
    from pathlib import Path

    import video_toolkit as vt
    import python_wizard as pw
    import py_string_tool as pst
    
    # alarm done path still have an error
    # took about 1 hr(including testing)
    # Add feature: input as video_folder_path and subtitle_folder_path, then 
    # it would automatically know which subttile to use with which video(using SxxExx)
    
    # split_audio_by_subtitle
    if prefix_name is None:
        prefix_name_in = Path(video_path).stem
    else:
        prefix_name_in = str(prefix_name)
        
    # with dot and no dots supported
    # but only tested with no dots out_audio_ext
    
    out_audio_ext_dot = out_audio_ext if out_audio_ext[0] == "." else ("." + out_audio_ext)
    out_audio_ext_no_dot = out_audio_ext[1:] if out_audio_ext[0] == "." else ( out_audio_ext)
    
    subs = vt.srt_to_df(subtitle_path)

    
    # TODO: write a function input is video/video path & subs/sub path
    t01 = time.time()
    video_audio = AudioSegment.from_file(video_path)
    t02 = time.time()
    t01_02 = t02-t01

    if verbose in [1]:
        print("Load video time: ", end = " ")
        pw.print_time(t01_02)
    
    if alarm_done:
        playsound(alarm_done_path)

    t03 = time.time()
    video_length = audio_duration(video_audio)
    # Iterate over subtitle sentences
    n = subs.shape[0]
    t04 = time.time()
    for i in range(n):
        start_time = subs.loc[i,'start']
        end_time = subs.loc[i,'end']
        sentence_text = subs.loc[i,'sentence']

        if start_time > video_length:
            break

        start_time_ms = to_ms(start_time)
        end_time_ms = to_ms(end_time)

        # Extract audio segment based on timestamps
        sentence_audio = video_audio[start_time_ms:end_time_ms]
        
        num_str = pst.num_format0(i+1,n+1)
        # Save the audio segment to a file
        if sentence_text[-1] in [".",","]:
            sentence_no_dots = sentence_text[:-1]
        else:
            sentence_no_dots = sentence_text

        if include_sentence:
            audio_name = f'{prefix_name_in}_{num_str}_{sentence_no_dots}{out_audio_ext_dot}'
        else:
            audio_name = f'{prefix_name_in}_{num_str}{out_audio_ext_dot}'
        
        audio_name_clean = pst.clean_filename(audio_name)
        audio_output = os.path.join(output_folder,audio_name_clean)
        sentence_audio.export(audio_output, format=out_audio_ext_no_dot)
    t05 = time.time()

    t04_05 = t05-t04
    if alarm_done:
        playsound(alarm_done_path)


def make_1_season_Excel_unaligned(EN_folder_path: Union[str,Path],
                                  PT_folder_path: Union[str,Path], 
                                  out_excel_name: Union[str,Path],
                                  output_folder = None,
                                  drop_timestamp = True,
                                  ):
    # medium tested
    # based on pd. 2.1.3
    # imported from NLP 09_SenMem Pipeline
    """
    

    Parameters
    ----------
    EN_folder_path : TYPE
        the path contains many Excel files of script in 1 episode(in English)
    PT_folder_path : TYPE
        the path contains many Excel files of script in 1 episode(in Portuguese)
    out_excel_name : TYPE
        DESCRIPTION.
    output_folder : TYPE
        DESCRIPTION.
     : TYPE
        DESCRIPTION.
    
    drop_timestamp: remove the timestamp from the output script
    (Not implemented)

    Returns
    -------
    out_df : TYPE
        DESCRIPTION.

    """
    import pandas as pd
    import sys
    from pathlib import Path

    
    import dataframe_short as ds
    import video_toolkit as vt
    import python_wizard as pw
    import os_toolkit as ost
    
    en_df = combine_files_1_season(str(EN_folder_path))
    en_df = en_df.add_suffix('_EN')
    # en_df.rename(columns = {'sentence':'sentence_EN',
    #                                 'start':'start_EN',
    #                                 'end':'end_EN',
    #                                 'NoSentence':'NoSentence_EN',
    #                                 },
    #              inplace = True,
                 
    #              )
    en_df["Episode"] = en_df["Episode_EN"]
    en_df = en_df.drop(columns = ["Episode_EN"])
    
    en_df['NoSentence_EN'] = en_df['NoSentence_EN'].astype('int')
    en_df['NoSentence_EN'] = en_df['NoSentence_EN'] + 1
    en_df = en_df.reset_index(drop = True)



    pt_df = combine_files_1_season(str(PT_folder_path))
    pt_df = pt_df.add_suffix('_PT')
    pt_df["Episode"] = pt_df["Episode_PT"]
    pt_df = pt_df.drop(columns = ["Episode_PT"])
    # pt_df.rename(columns = {'sentence':'sentence_PT',
    #                                 'start':'start_PT',
    #                                 'end':'end_PT',
    #                                 'NoSentence':'NoSentence_PT',
    #                                 },
    #              inplace = True,
    #              )
    pt_df['NoSentence_PT'] = pt_df['NoSentence_PT'].astype('int')
    pt_df['NoSentence_PT'] = pt_df['NoSentence_PT'] + 1
    pt_df = pt_df.reset_index(drop = True)

    out_df:pd.DataFrame

    pt_df_music = pt_df[pt_df['sentence_PT'].str.contains('♪', na=False) ]
    en_df_music = en_df[en_df['sentence_EN'].str.contains('♪', na=False) ]


    # Filter out rows where 'Column1' contains '♪'
    en_df_filter = en_df[~en_df['sentence_EN'].str.contains('♪', na=False)]
    pt_df_filter = pt_df[~pt_df['sentence_PT'].str.contains('♪', na=False)]
    en_df_music = en_df_filter[en_df_filter['sentence_EN'].str.contains('♪', na=False) ]


    out_df = ds.index_aligned_append(en_df_filter,pt_df_filter,"Episode")
    out_df = out_df.reset_index(drop = True)
    out_df.index = out_df.index + 1
    # keep only the first occurrence of each column (Episode is duplicated)
    out_df = out_df.loc[:, ~out_df.columns.duplicated()]
    
    # automatically add .xlsx extension to the file 
    out_excel_name_in = out_excel_name if ".xlsx" in out_excel_name else (out_excel_name + ".xlsx")
    
    ds.move_col_front(out_df, "Episode")
    
    if output_folder is None:
        out_excel_path = str(out_excel_name_in)
    else:
        out_excel_path = str(Path(output_folder) / Path(out_excel_name_in))
    
    if drop_timestamp:
        out_df = out_df.drop(columns = ['start_EN','end_EN','start_PT','end_PT'])
    
    out_df['Episode'] = out_df['Episode'].ffill()
    out_df.to_excel(str(out_excel_path))
    
    return out_df

# read the link here of how to use Lingtrain
# https://habr.com/ru/articles/586574/

def read_sentences_from_excel(file_path, sheet_name, portuguese_col, english_col, nrows=None):
    # imported from NLP 09_SenMem Pipeline
    """
    Reads Portuguese and English sentences from an Excel file.
    
    :param file_path: Path to the Excel file.
    :param sheet_name: Name of the sheet containing the sentences.
    :param portuguese_col: Column letter for Portuguese sentences.
    :param english_col: Column letter for English sentences.
    :return: Tuple of two lists containing Portuguese and English sentences.
    """

    df = ds.pd_read_excel(file_path,sheet_name=sheet_name,nrows=nrows,usecols=[portuguese_col,english_col])

    portuguese_sentences = df.iloc[:,0].tolist()
    english_sentences = df.iloc[:,1].tolist()


    return portuguese_sentences, english_sentences

    
def read_movie_script2(file_path, sheet_name = "Sheet1", portuguese_col = 0, english_col = 1):
    # imported from NLP 09_SenMem Pipeline
    # middle tested 
    # dependency: pd_by_column, pd_split_into_dict_df, pd_regex_index
    # work with format that use title to seperate the episode
    import pandas as pd
    import re
    from openpyxl.utils import column_index_from_string
    
    # Load the dataset from the Excel file
    
    if pw.is_convertible_to_num(portuguese_col):
        portuguese_col_no = int(portuguese_col)
    else:
        portuguese_col_no = column_index_from_string(portuguese_col) - 1
        
    
    if pw.is_convertible_to_num(english_col):
        english_col_no = int(english_col)
    else:
        english_col_no = column_index_from_string(english_col) - 1
    
    # If it's the column name eg A, G,H
    
    data_ori = ds.pd_read_excel(file_path, sheet_name=sheet_name)
    # playsound(alarm_path)
    
    data = ds.pd_by_column(data_ori,[portuguese_col_no, english_col_no])
    

    # Function to check if a cell value matches the episode identifier pattern (e.g., S01E01)
    # r'[Ss]\d{2}[Ee]\d{2}' => S01E01
    df_dict = ds.pd_split_into_dict_df(data,r'[Ss]\d{2}[Ee]\d{2}',0)
    # df_dict = pd_split_into_dict_df(data,index_list=episode_start_indices)
    return df_dict

def read_movie_script(file_path, sheet_name, portuguese_col, english_col):
    # the main function that I should use from now on
    # imported from NLP 09_SenMem Pipeline
    from openpyxl.utils import column_index_from_string
    df = ds.pd_read_excel(file_path, sheet_name=sheet_name)
    # df = pd_by_column(df_ori, [portuguese_col,english_col])
    import pandas as pd
    """
    Extracts content from a DataFrame based on 'Episode' information.

    Parameters
    ----------
    df : pandas.DataFrame
        The original DataFrame containing an 'Episode' column with format 'SxxExx',
        and columns for content ('sentence_PT', 'sentence_EN').

    Returns
    -------
    pandas.DataFrame
        A new DataFrame with 'season' and 'episode' as MultiIndex.
        Each row contains a DataFrame in the 'content' column, which itself
        contains 'sentence_PT' and 'sentence_EN' from the original DataFrame.

    Examples
    --------
    >>> main_df = pd.DataFrame({
    ...     'Episode': ['S06E08', 'S06E08', 'S01E01'],
    ...     'sentence_PT': ['sentence1_PT', 'sentence2_PT', 'sentence3_PT'],
    ...     'sentence_EN': ['sentence1_EN', 'sentence2_EN', 'sentence3_EN']
    ... })
    >>> read_movie_script2(main_df)
    """
    
    if pw.is_convertible_to_num(portuguese_col):
        portuguese_col_no = int(portuguese_col)
    else:
        portuguese_col_no = column_index_from_string(portuguese_col) - 1
        
    
    if pw.is_convertible_to_num(english_col):
        english_col_no = int(english_col)
    else:
        english_col_no = column_index_from_string(english_col) - 1
    
    # Extract season and episode numbers from the 'Episode' column
    df['season'] = df['Episode'].str.extract(r'S(\d+)E\d+').astype(int)
    df['episode'] = df['Episode'].str.extract(r'S\d+E(\d+)').astype(int)
    
    # Prepare the data for the new DataFrame
    data = []
    
    # Group by 'season' and 'episode', then iterate over each group
    for (season, episode), group in df.groupby(['season', 'episode']):
        # Create a DataFrame for this group's content
        content_df = ds.pd_by_column(group, [portuguese_col_no, english_col_no]).reset_index(drop=True)
        
        # Append season, episode, and content DataFrame to the list
        data.append({'season': season, 'episode': episode, 'content': content_df})
    
    # Convert the list to a DataFrame
    new_df = pd.DataFrame(data)
    
    # Set 'season' and 'episode' as the index
    new_df.set_index(['season', 'episode'], inplace=True)
    
    return new_df


def align_1_season(excel_1_season_script,
                   out_excel_name: Union[str,Path],
                   output_folder = None,
                   sheet_name = 'Sheet1',
                   
                   n_episodes: Union[str,int] = "all",
                   portuguese_col = "F",
                   english_col = "D",
                   lang_from="PT",
                   lang_to="EN",
                   alarm_done:bool = True,
                   
                   ) -> pd.DataFrame:
    
    # imported from NLP 09_SenMem Pipeline
    """
    
    it would take about 1.2 min per 1 episode of BigBang(20 min)
    about 20 min in 1 whole season
    
    create the Excel file for "aligned" sentences for 1 season for series

    Parameters
    ----------
    excel_1_season_script : TYPE
        Excel that has 1 sheet containing all episodes script
        
    out_excel_name : Union[str,Path]
        output Excel name, only ".xlsx" supported at the moment
        
    output_folder : TYPE, optional
        DESCRIPTION. The default is None.
    sheet_name : TYPE, optional
        DESCRIPTION. The default is 'Sheet1'.
    portuguese_col : TYPE, optional
        DESCRIPTION. The default is "F".
    english_col : TYPE, optional
        DESCRIPTION. The default is "D".
    lang_from : TYPE, optional
        DESCRIPTION. The default is "PT".
    lang_to : TYPE, optional
        DESCRIPTION. The default is "EN".

    Returns
    -------
    you need to set this saved as variable otherwise it would output df.head()
    it would export the Excel file and return pd.df at the same time
    pd.DataFrame

  """
    
    import pandas as pd
    import time
    from playsound import playsound
    from tqdm import tqdm
    
    episode_aligned: pd.DataFrame
    
    ts_start = time.perf_counter()
    
    df_script = read_movie_script(excel_1_season_script, sheet_name, portuguese_col, english_col)
    season_aligned = pd.DataFrame()
    ts_read  = time.perf_counter()
    error_episode = []
    
    
    
    # using 1-index system
    i = 1
    for curr_index in df_script.index:
        
        if isinstance(n_episodes, int):
            if i > n_episodes:
                break
            
        season, episode = curr_index
        episode_str = f'S{season:02d}E{episode:02d}'
        single_episode = df_script.loc[curr_index,"content"]
        
        try:
            
            # slow from here
            episode_aligned = sen_alignment_df(single_episode,lang_from=lang_from,lang_to=lang_to,alarm = False)
    
            episode_aligned.index = episode_aligned.index + 1
            episode_aligned['sentence_' + lang_from  ] = episode_aligned[lang_from]
            episode_aligned['sentence_' + lang_to  ] = episode_aligned[lang_to]
            
            episode_aligned = episode_aligned.drop(columns = [lang_from,lang_to])
            
            episode_aligned['Season'] =  season
            episode_aligned['Episode'] =  episode
            episode_aligned = episode_aligned.drop_duplicates(subset=['sentence_' + lang_from ,'sentence_' + lang_to])
            ds.move_col_front(episode_aligned, ['Season','Episode'])
            # drop rows that are empty
            episode_aligned = episode_aligned.dropna(subset = ['sentence_' + lang_from] )
            
            season_aligned = pd.concat([season_aligned,episode_aligned])
            print(f"{episode_str} Done Aligning !!! ----------------------------------------")
        except:
            print(f"Error at {episode_str} was found !!! ########################")
            error_episode.append(episode_str)
        
        i += 1
            
    out_excel_name_in = out_excel_name if ".xlsx" in out_excel_name else (out_excel_name + ".xlsx")
    
    
    if output_folder is None:
        out_excel_path = str(out_excel_name_in)
    else:
        out_excel_path = str(Path(output_folder) / Path(out_excel_name_in))
    season_aligned.to_excel(str(out_excel_path))
    
    if len(error_episode) > 0:
        print("Errors occurred at these episodes")
        print(error_episode)
    
    ts_end = time.perf_counter()
    duration_read = ts_read - ts_start
    total_duration = ts_end - ts_start
    # i = counted episodes
    
    avg_per_ep = total_duration / i
    avg_per_ep /= 60

    print("\nTotal processing time")
    pw.print_time(total_duration)
    
    print(f"{avg_per_ep:.2f} min per episode\n")    
    if alarm_done:
        playsound(alarm_done_path)
    
    return season_aligned


def sen_alignment_df(df, lang_from = None, lang_to = None,
                       alarm_done:bool = True,
                     ):
    # medium tested
    if lang_from is None: lang_from = df.columns[0]
    if lang_to is None: lang_to = df.columns[1]
    
    text_list_from = df.iloc[:, 0].tolist()
    text_list_to = df.iloc[:, 1].tolist()
    # assume that text from is
    result = sentence_alignment(text_list_from,text_list_to,lang_from,lang_to,alarm_done=alarm_done)
    
    return result
    

def sentence_alignment(text_from,text_to, lang_from = "pt", lang_to = "en",
                       alarm_done:bool = True,
                       
                       ):
    # v02 => add alarm parameter
    # text_from, text_to are expected to be text or list
    # medium tested, seem to work pretty well now
    
    import os
    from lingtrain_aligner import preprocessor, splitter, aligner, resolver, reader, helper, vis_helper
    from pathlib import Path
    import lingtrain_aligner
    from playsound import playsound
    import numpy as np
    from time import time
    

    folder = Path.cwd()
    db_name = "book.db"
    
    db_path = folder / db_name

    
    models = ["sentence_transformer_multilingual", "sentence_transformer_multilingual_labse"]
    model_name = models[0]
    
    # convert to list of text_from,text_to is not list
    
        
    ts01 = time()
    if not isinstance(text_from, list):
        text1_prepared = preprocessor.mark_paragraphs(text_from)
        splitted_from = splitter.split_by_sentences_wrapper(text1_prepared, lang_from)
    else:
        splitted_from = [str(x) for x in text_from if x is not np.nan ]
        # splitted_from = splitter.split_by_sentences_wrapper(text_from, lang_from)
    
    if not isinstance(text_to, list):
        
        text2_prepared = preprocessor.mark_paragraphs(text_to)
        splitted_to = splitter.split_by_sentences_wrapper(text2_prepared, lang_to)
    else:
        splitted_to = [str(x) for x in text_to if x is not np.nan ]
        # splitted_to = splitter.split_by_sentences_wrapper(text_to, lang_to)

    # temp adding title, author, h1, h2 to make it work first,.... we'll look into it when this is not avaliable later
    
    
    # if lang_from == "pt" and lang_to == "en":
    #     marker = ["(No title)%%%%%title." , 
    #                "(No author)%%%%%author.", 
    #                "(No header_)%%%%%h1.", 
    #                "(No header_)%%%%%h2."]
    #     splitted_from = marker + splitted_from
    #     splitted_to = marker + splitted_to
        
        
    # Create the database and fill it.
    if os.path.isfile(db_path):
        os.unlink(db_path)
        
    aligner.fill_db(db_path, lang_from, lang_to, splitted_from, splitted_to)
    
    # batch_ids = [0,1]
    
    aligner.align_db(db_path, \
                    model_name, \
                    batch_size=100, \
                    window=40, \
                    # batch_ids=batch_ids, \
                    save_pic=False,
                    embed_batch_size=10, \
                    normalize_embeddings=True, \
                    show_progress_bar=True
                    )
    pic_name = "alignment_vis.png"
    pic_path = folder / pic_name
    vis_helper.visualize_alignment_by_db(db_path, output_path=pic_path, lang_name_from=lang_from, lang_name_to=lang_to, batch_size=400, size=(800,800), plt_show=True)
    
    # Explore the conflicts
    
    conflicts_to_solve, rest = resolver.get_all_conflicts(db_path, min_chain_length=2, max_conflicts_len=6, batch_id=-1)
    
    resolver.get_statistics(conflicts_to_solve)
    resolver.get_statistics(rest)
    
    # resolver.show_conflict(db_path, conflicts_to_solve[8])
    
    
    steps = 10
    batch_id = -1 
    
    for i in range(steps):
        conflicts, rest = resolver.get_all_conflicts(db_path, min_chain_length=2+i, max_conflicts_len=6*(i+1), batch_id=batch_id)
        resolver.resolve_all_conflicts(db_path, conflicts, model_name, show_logs=False)
        vis_helper.visualize_alignment_by_db(db_path, output_path="img_test1.png", lang_name_from=lang_from, lang_name_to=lang_to, batch_size=400, size=(600,600), plt_show=True)
    
        if len(rest) == 0: break
    
    paragraphs = reader.get_paragraphs(db_path)[0]
    
    paragraph_from_2D = paragraphs['from']
    paragraph_to_2D = paragraphs['to']

    paragraph_from_result = [item for list_1D in paragraph_from_2D for item in list_1D]
    paragraph_to_result = [item for list_1D in paragraph_to_2D for item in list_1D]
    
    paragraph_result = pd.DataFrame({lang_from:paragraph_from_result,
                                     lang_to:paragraph_to_result
                                     })
    
    ts02 = time()
    total_time = ts02-ts01
    pw.print_time(total_time)
    
    if alarm_done:
        playsound(alarm_done_path)
    
    return paragraph_result


def combine_files_1_season(folder_path):
    from functools import partial
    import dataframe_short as ds
    
    func = partial(ds.combine_files_to_df, 
                   extract_pattern = r'S\d+E\d+',
                   filename_col_name = "Episode",
                   )
    out_df = func(folder_path)
    out_df.columns.values[1] = 'NoSentence'
    return out_df


def crop_video(
        video_path: str, 
        t_start: str, 
        t_end: str, 
        time_slice: List[Tuple[str, str]],
        output_extension: Literal["mp3", ".mp3",".mp4","mp4","mkv",".mkv","wav",".wav"] = None,
        alarm_done = True
        ):
    # tested only input(mkv) => output(mkv)
    import subprocess
    import os
    from playsound import playsound
    
    
    # Construct the base output filename
    base_name = os.path.splitext(video_path)[0]
    
    if output_extension is None:
        extension_in = os.path.splitext(video_path)[1][1:]
    else:
        extension_in = (output_extension.split(".")[1]) if "." in output_extension else output_extension
    # Find an unused file name
    i = 1
    while os.path.exists(f"{base_name}_{i:02d}.{extension_in}"):
        i += 1
    output_path = f"{base_name}_{i:02d}.{extension_in}"
    # FFmpeg command
    command = [
        'ffmpeg', '-ss', t_start, '-to', t_end,
        '-i', video_path,
        '-c', 'copy' if extension_in in ["mp4","mkv"] else '-vn',
        output_path
    ]
    
    result = subprocess.run(command, text=True, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print("Error encountered:")
        print(result.stderr)
    
    elif result.returncode == 0:
        print("Extract audio successfully!!!")
        
        if alarm_done:
            playsound(alarm_done_path)
    
    return output_path  # Return the output file path


def srt_to_df(srt_path,
              remove_stopwords=True,
              stopwords = ["♪","\n","<i>","</i>","<b>","</b>"]):
# remove_newline will remove '\n' from the extracted text
    import pysrt
    import pandas as pd
    import py_string_tool as pst
    import os_toolkit as ost

    if ".srt" in str(srt_path):
        # 1 file case
        subs = pysrt.open(srt_path)
        # Initialize empty lists for storing data
        sentences = []
        start_times = []
        end_times = []
    
        # Extract data from each subtitle sentence
        for sub in subs:
            sentences.append(sub.text)
            start_times.append(sub.start.to_time())
            end_times.append(sub.end.to_time())
    
        # Create a DataFrame
        if remove_stopwords:
            #FIX it's still can't replace properly 
            sentences = [pst.replace(sentence,stopwords,"") for sentence in sentences]
        df = pd.DataFrame({
            'sentence': sentences,
            'start': start_times,
            'end': end_times
        })
        return df
    else:
        # many srt's file using folder
        str_file_names = ost.get_full_filename(srt_path,".srt")
        df_list = []
        for str_file_name in str_file_names:
            each_df = srt_to_df(str_file_name)
            df_list.append(each_df)
        return df_list


def srt_to_csv(srt_path,output_path,encoding='utf-8-sig',index=False):
    # output should be total_path
    df_sub = srt_to_df(srt_path)
    # encoding='utf-8-sig' for Portuguese
    df_sub.to_csv(output_path, encoding=encoding,index=index)

def srt_to_Excel(srt_path,output_path,encoding='utf-8-sig',index=True):
    import pandas as pd
    import os
    """ 
    Wrote on Aug 27, 2023
    I already wrote it for 1 file but it took me about 3 additional hrs to 
    make it work with multiple files in folder
    """
    # output should be total_path
    df_sub = srt_to_df(srt_path)
    pd_ver = pw.package_version("pandas")
    
    if isinstance(df_sub,pd.DataFrame):
    # encoding='utf-8-sig' for Portuguese
        if pd_ver < (2,0,0):
            df_sub.to_excel(output_path, encoding=encoding,index=index)
        else:
            df_sub.to_excel(output_path, index=index)
            
    elif isinstance(df_sub,list):
        short_names = ost.get_filename(srt_path,".srt")
        out_full_name = [os.path.join(output_path,short_name).replace(".srt",".xlsx") for short_name in short_names]
        
        if pd_ver < (2,0,0):
            df_sub.to_excel(output_path, encoding=encoding,index=index)
            for i,df in enumerate(df_sub):
                df.to_excel(out_full_name[i], encoding=encoding,index=index)
                
        else:
            for i,df in enumerate(df_sub):
                df.to_excel(out_full_name[i], index=index)

def to_ms(time_obj: datetime.time) -> float:
    time_obj_ms = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 1000 + time_obj.microsecond // 1000
    return time_obj_ms

# from typing import Union,List,Tuple, Literal, Callable, Dict
# from pathlib import Path
# import sys
# import datetime
# import python_wizard as pw
# import os_toolkit as ost
# import dataframe_short as ds
# import pkg_resources

del Union
del List
del Tuple
del Literal
del Callable
del Dict

# TODO: srt_to_Excel => similar to srt_to_csv but output as excel
# srt_to_Excel(srt_path,sub_output)

# n_file = len(srt_to_df(srt_folder_path))
# srt_to_Excel(srt_folder_path,output_folder)

# print(f"Done converting srt to Excel in Total {n_file} files ")
# playsound(alarm_path)




