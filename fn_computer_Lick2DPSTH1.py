def fn_computer_Lick2DPSTH2(key, self, rel_data, fr_interval, fr_interval_limit, flag_electric_video, time_resample_bin, session_epoch_type, session_epoch_number, self2, self3, self4):
    import datajoint as dj
    import numpy as np
    import scipy as scipy
    import scipy.stats
    from scipy import signal
    from scipy import stats as st
    from scipy.stats import ranksums, pearsonr
    from datajoint import fetch
    from fn_parse_into_trials_and_get_lickrate import fn_parse_into_trials_and_get_lickrate1
    from scipy.ndimage import convolve1d


    img= dj.schema('arseny_learning_imaging')
    img= dj.VirtualModule('IMG', 'arseny_learning_imaging')
    #imgframstarttrail= imgframstarttrail1.IMG.FramStartTrail

    tracking= dj.schema('arseny_learning_tracking')
    tracking= dj.VirtualModule('TRACKING', 'arseny_learning_tracking')
    #grooming= tracking.VideoGroomingTrail

    exp2= dj.schema('arseny_s1alm_experiment2')
    exp2= dj.VirtualModule ('EXP2', 'arseny_s1alm_experiment2')
    #behaviortrail= exp2vm.BehaviorTrial
    #behaviortrailevent= exp2vm.BehaviorTrailEvent
    #actionevent= exp2vm.ActionEvent

    lick2dtalp= dj.schema('talch012_lick2dtalp')
    lick2dtal= dj.VirtualModule('Lick2DtalP', 'talch012_lick2dtalp')

    # frames for PSTH
    smooth_window_sec = 0.2
    session_epoch_type= (session_epoch_type)
    session_epoch_number= (session_epoch_number)
    # fetch data
    rel_ROI = (img.ROI - img.ROIBad) & key # roi bad are bad ROI that were considered cell by suite2p
    # key_ROI1 = rel_ROI.fetch(order_by='roi_number')
    # key_ROI2 = rel_ROI.fetch(order_by='roi_number')
    # key_ROI3 = rel_ROI.fetch(order_by='roi_number')
    # key_ROI4 = rel_ROI.fetch(order_by='roi_number')
    #trydict=rel_ROI.fetch(as_dict=True)
    key_ROI1=rel_ROI.fetch("KEY", order_by='roi_number')
    key_ROI2=rel_ROI.fetch("KEY", order_by='roi_number')
    key_ROI3=rel_ROI.fetch("KEY", order_by='roi_number')
    key_ROI4=rel_ROI.fetch("KEY", order_by='roi_number')

    rel_data = rel_data & rel_ROI & key
  
    try:
        frame_rate = (img.FOVEpoch & key).fetch1('imaging_frame_rate')
    
    except:
    # If not found, try fetching from IMG.FOV
        frame_rate = (img.FOV & key).fetch1('imaging_frame_rate')
    # if result:
    #     frame_rate = result[0]
        
    smooth_window_frames = int(np.ceil(smooth_window_sec * frame_rate))  # frames for PSTH, Rounds toward positive infinity 

    # fetch trial data
    R = ((exp2.TrialRewardSize & key) - tracking.VideoGroomingTrial).fetch(order_by='trial')
    Block= ((exp2.TrialLickBlock & key)- tracking.VideoGroomingTrial).fetch(order_by='trial')
    #Block = fetch((exp2.TrialLickBlock & key) - tracking.VideoGroomingTrial, '*', order_by='trial')
    # S = rel_data.fetch() #rel_data comes from the table definition, it refers to ROISpikes (flourescent trace) that calculates the spikes_trace which is deconvolved trace for each frame 
    # if 'spikes_trace' in S:  # to be able to run the code both on dff and on deconvulted "spikes" data
    #     S['dff_trace'] = S['spikes_trace'] #dff_trace is a defined key
    #     del S['spikes_trace']
    # Fetch the original DataJoint table
    # Fetch 'rel_data' into 'S'
    S = rel_data.fetch()
    # # Check if 'spikes_trace' exists in 'S'
    # if 'spikes_trace' in S.dtype.names:
    #     # Create 'dff_trace' column in 'S' and assign 'spikes_trace' values to it
    #     S['dff_trace'] = S['spikes_trace']

    #     # Remove 'spikes_trace' column from 'S'
    #     S = S.drop('spikes_trace')
    S = rel_data.fetch(as_dict=True)

    if 'spikes_trace' in S[0]:
        for row in S:
            row['dff_trace'] = row.pop('spikes_trace')
            row.pop('spikes_trace', None)
    else:
        pass

    start_file, end_file, lick_tr_times_relative_to_first_lick_after_go, lick_tr_total = fn_parse_into_trials_and_get_lickrate1(key, frame_rate, fr_interval, flag_electric_video)
    start_file[-1] = float('nan')
    end_file[-1] = float('nan')
    num_trials = len(start_file)
    idx_response = ~np.isnan(start_file)
    
    try:
        # idx reward
        idx_regular = np.where((R['reward_size_type'] == 'regular') & idx_response)[0]
        idx_regular_temp = (R['reward_size_type'] == 'regular') & idx_response
        idx_small = np.where((R['reward_size_type'] == 'omission') & idx_response)[0]
        idx_large = np.where((R['reward_size_type'] == 'large') & idx_response)[0]
        
     
        idx_odd_small = idx_regular[0::2][:len(idx_small)]
        idx_even_small = idx_regular[1::2][:len(idx_small)]

        idx_odd_large = idx_regular[0::2][:len(idx_large)]
        idx_even_large = idx_regular[1::2][:len(idx_large)]

    except:
        idx_regular = np.where(np.arange(1, num_trials + 1) & idx_response)[0]
        idx_regular_temp = np.arange(1, num_trials + 1) & idx_response

    # idx_odd_regular = idx_regular[::2][:len(idx_regular)]
    # idx_even_regular = idx_regular[1::2][:len(idx_regular)//2]

    idx_odd_regular = idx_regular[0::2]
    idx_even_regular = idx_regular[1::2]
    
    try:
        # devied the block to 4 bins according to the current_trial_number_in_block- the first trial are defined as first all the first trials, and the three others inbetween the bins values defined
        # find the most frequent num_trials_in_block. in matlab we use mode(), in python we can use statistics.mode() but here we use bincount to count each value and returns the highest count value. note that in both (python&matlab) cases it returns the first mode he founds (meaning if you have two most freq values, it returns the first that appeared) 
        # we devied the regular but no small/large as regular are 80% of the data. 
        num_trials_in_block = np.bincount(Block['num_trials_in_block']).argmax()
        begin_mid_end_bins = np.linspace(2, num_trials_in_block, 4)# returns 4 values the first is 2, the last is num_trials_in_block and the two middel ones are num_trials_in_block-(num_trials_in_block-2)/3 and ans-(num_trials_in_block-2)/3

        idx_first = np.where((np.array(Block['current_trial_num_in_block']) == 1) & idx_response & idx_regular_temp)[0] #indexes of the current trail in block==1&not nan& ind of the 01 map of regular reward
        idx_begin = np.where((np.array(Block['current_trial_num_in_block']) >= begin_mid_end_bins[0]) & (np.array(Block['current_trial_num_in_block']) <= np.floor(begin_mid_end_bins[1])) & idx_response & idx_regular_temp)[0]
        idx_mid = np.where((np.array(Block['current_trial_num_in_block']) > begin_mid_end_bins[1]) & (np.array(Block['current_trial_num_in_block']) <= np.round(begin_mid_end_bins[2])) & idx_response & idx_regular_temp)[0]
        idx_end = np.where((np.array(Block['current_trial_num_in_block']) > begin_mid_end_bins[2]) & (np.array(Block['current_trial_num_in_block']) <= np.ceil(begin_mid_end_bins[3])) & idx_response & idx_regular_temp)[0]

        idx_odd_first = idx_first[::2]
        idx_even_first = idx_first[1::2]

        idx_odd_begin = idx_begin[::2]
        idx_even_begin = idx_begin[1::2]

        idx_odd_mid = idx_mid[::2]
        idx_even_mid = idx_mid[1::2]

        idx_odd_end = idx_end[::2]
        idx_even_end = idx_end[1::2]
    except:
        pass
            
    
    # we take the session epoch type and number of the current key (one iteration) and apply it to the coresponding possition in each key_ROI(i). we are going to use key_ROI for####
        #SI=np.array(S)
    for i_roi in range(len(key_ROI1)):
        key_ROI1[i_roi]['session_epoch_type'] = key['session_epoch_type']
        key_ROI1[i_roi]['session_epoch_number'] = key['session_epoch_number']
        key_ROI2[i_roi]['session_epoch_type'] = key['session_epoch_type']
        key_ROI2[i_roi]['session_epoch_number'] = key['session_epoch_number']
        key_ROI3[i_roi]['session_epoch_type'] = key['session_epoch_type']
        key_ROI3[i_roi]['session_epoch_number'] = key['session_epoch_number']
        key_ROI4[i_roi]['session_epoch_type'] = key['session_epoch_type']
        key_ROI4[i_roi]['session_epoch_number'] = key['session_epoch_number']
        # for i_roi in range(len(S)):
        
        ## make a new table with session epoch type and number (created in a loop assigning the i_roi key value), add this table to key_roi# 

        # key_ROI1 = key_ROI1.tolist()
        # key_ROI2 = key_ROI2.tolist()
        # key_ROI3 = key_ROI3.tolist()
        # key_ROI4 = key_ROI4.tolist()
        # key_ROI1[i_roi]['session_epoch_type'] = session_epoch_type
        # key_ROI1[i_roi]['session_epoch_number'] = session_epoch_number
        # key_ROI2[i_roi]['session_epoch_type'] = session_epoch_type
        # key_ROI2[i_roi]['session_epoch_number'] = session_epoch_number
        # key_ROI3[i_roi]['session_epoch_type'] = session_epoch_type
        # key_ROI3[i_roi]['session_epoch_number'] = session_epoch_number
        # key_ROI4[i_roi]['session_epoch_type'] = session_epoch_type
        # key_ROI4[i_roi]['session_epoch_number'] = session_epoch_number

        # key_ROI1 = dict(session_epoch_type=key['session_epoch_type'], session_epoch_number=key['session_epoch_number'])
        # key_ROI2 = dict(session_epoch_type=key['session_epoch_type'], session_epoch_number=key['session_epoch_number'])
        # key_ROI3 = dict(session_epoch_type=key['session_epoch_type'], session_epoch_number=key['session_epoch_number'])
        # key_ROI4 = dict(session_epoch_type=key['session_epoch_type'], session_epoch_number=key['session_epoch_number'])
        # key_ROI1 = np.array(key_ROI1)
        # key_ROI2 = np.array(key_ROI2)
        # key_ROI3 = np.array(key_ROI3)
        # key_ROI4 = np.array(key_ROI4)
        
        # key_ROI1[i_roi]['session_epoch_type'] = key['session_epoch_type']
        # key_ROI1[i_roi]['session_epoch_number'] = key['session_epoch_number']

        # key_ROI2[i_roi]['session_epoch_type'] = key['session_epoch_type']
        # key_ROI2[i_roi]['session_epoch_number'] = key['session_epoch_number']

        # key_ROI3[i_roi]['session_epoch_type'] = key['session_epoch_type']
        # key_ROI3[i_roi]['session_epoch_number'] = key['session_epoch_number']

        # key_ROI4[i_roi]['session_epoch_type'] = key['session_epoch_type']
        # key_ROI4[i_roi]['session_epoch_number'] = key['session_epoch_number']

        # Use key_ROI1, key_ROI2, key_ROI3, key_ROI4 as needed
        # Perform further operations or insert into DataJoint tables

        #PSTH 
        # spikes = S[i_roi]['dff_trace']
        # time = []        
        # time_new = []
        # psth_all = [None] * len(start_file)
        # if not time_resample_bin:
        #     # psth_all = [None] * len(start_file)
        #     for i_tr in range(num_trials):
        #         if idx_response[i_tr] == False:  # It's an ignore trial
        #             psth_all[i_tr] = np.nan
        #             continue
        #         # nan_placeholder = -1
        #         # start_file = [int(x) if not np.isnan(x) else nan_placeholder for x in start_file]
        #         # end_file = [int(x) if not np.isnan(x) else nan_placeholder for x in end_file]
        #         # s = [None] * len(15)
        #         if start_file[i_tr] != -1 and not np.isnan(start_file[i_tr]) and end_file[i_tr] != -1 and not np.isnan(end_file[i_tr]):
        #             s = spikes[start_file[i_tr]:end_file[i_tr]]
        #             s = np.convolve(s, np.ones(smooth_window_frames) / smooth_window_frames, mode='valid')
        #             time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
        #             psth_all[i_tr] = s
        # else:
        #     if time_resample_bin:  # Add condition to handle empty time_resample_bin
        #         time_new_bins = np.arange(fr_interval[0], fr_interval[-1], time_resample_bin)
        #         time_new = time_new_bins[:-1] + np.mean(np.diff(time_new_bins)) / 2

        #         for i_tr in range(len(start_file)):
        #             if idx_response[i_tr] == False:  # It's an ignore trial
        #                 psth_all[i_tr] = np.nan
        #                 continue
        #             # nan_placeholder = -1
        #             # start_file = [int(x) if not np.isnan(x) else nan_placeholder for x in start_file]
        #             # end_file = [int(x) if not np.isnan(x) else nan_placeholder for x in end_file]
        #             if start_file[i_tr] != -1 and not np.isnan(start_file[i_tr]) and end_file[i_tr] != -1 and not np.isnan(end_file[i_tr]):
        #                 s = spikes[start_file[i_tr]:end_file[i_tr]]
        #                 s = np.convolve(s, np.ones(smooth_window_frames) / smooth_window_frames, mode='same')
        #             # time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
        #             # s_resampled = []

        #             # for i_t in range(len(time_new_bins) - 1):
        #             #     idx_t = (time > time_new_bins[i_t]) & (time <= time_new_bins[i_t + 1])
        #             #     s_resampled.append(np.mean(s[idx_t]))

        #             # psth_all[i_tr] = s_resampled
        #                 time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
        #                 s_resampled = np.interp(time_new, time, s)
        #                 psth_all.append(s_resampled)
        #     time = time_new

        #spikes = S[i_roi]['dff_trace']
        time = []
        time_new = []
        psth_all = [np.nan] * len(start_file)
        spikes = list(S[i_roi]['dff_trace'])
        if not time_resample_bin:
            for i_tr in range(num_trials):
                if idx_response[i_tr] == False:  # It's an ignore trial
                    psth_all[i_tr] = np.nan
                    continue

                if not np.isnan(start_file[i_tr]) and not np.isnan(end_file[i_tr]):
                    start_idx = int(start_file[i_tr]) if not np.isnan(start_file[i_tr]) else 0
                    end_idx = int(end_file[i_tr]) if not np.isnan(end_file[i_tr]) else len(spikes)
                    #spikes=spikes.tolist()
                    #spikes=spikes[0] # return a simple list you can work with directly, len remain the same
                    s = spikes[0][start_idx:end_idx]#.astype(np.float32)
                    s = convolve1d(s, weights=np.ones(smooth_window_frames) / smooth_window_frames, mode='constant', cval=np.nan)
                    #s = np.convolve(s, np.ones(smooth_window_frames) / smooth_window_frames, mode='valid')
                    time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
                    psth_all[i_tr] = s[:len(s)].tolist()
        else:
            if time_resample_bin:  # Add condition to handle empty time_resample_bin
                time_new_bins = np.arange(fr_interval[0], fr_interval[-1], time_resample_bin)
                time_new = time_new_bins[:-1] + np.mean(np.diff(time_new_bins)) / 2

                for i_tr in range(len(start_file)):
                    if idx_response[i_tr] == False:  # It's an ignore trial
                        psth_all[i_tr] = np.nan
                        continue

                    if not np.isnan(start_file[i_tr]) and not np.isnan(end_file[i_tr]):
                        start_idx = int(start_file[i_tr]) if not np.isnan(start_file[i_tr]) else 0
                        end_idx = int(end_file[i_tr]) if not np.isnan(end_file[i_tr]) else len(spikes)
                        s = spikes[0, start_idx:end_idx].astype(np.float32)
                        s = np.convolve(s, np.ones(smooth_window_frames) / smooth_window_frames, mode='same')
                        time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
                        s_resampled = np.interp(time_new, time, s)
                        psth_all.append(s_resampled[:len(s)])

            time = time_new

        # spikes = S[i_roi]['dff_trace']
        # time = []
        # time_new = []
        # psth_all = [None] * len(start_file)

        # if not time_resample_bin:
        #     for i_tr in range(num_trials):
        #         if idx_response[i_tr] == False:  # It's an ignore trial
        #             psth_all[i_tr] = np.nan
        #             continue

        #         if not np.isnan(start_file[i_tr]) and not np.isnan(end_file[i_tr]):
        #             start_idx = int(start_file[i_tr]) if not np.isnan(start_file[i_tr]) else 0
        #             end_idx = int(end_file[i_tr]) if not np.isnan(end_file[i_tr]) else len(spikes)
        #             s = spikes[start_idx:end_idx].astype(np.float32)  # Convert to float32
        #             s = np.convolve(s, np.ones(smooth_window_frames) / smooth_window_frames, mode='valid')
        #             time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
        #             psth_all[i_tr] = s
        # else:
        #     if time_resample_bin:  # Add condition to handle empty time_resample_bin
        #         time_new_bins = np.arange(fr_interval[0], fr_interval[-1], time_resample_bin)
        #         time_new = time_new_bins[:-1] + np.mean(np.diff(time_new_bins)) / 2

        #         for i_tr in range(len(start_file)):
        #             if idx_response[i_tr] == False:  # It's an ignore trial
        #                 psth_all[i_tr] = np.nan
        #                 continue

        #             if not np.isnan(start_file[i_tr]) and not np.isnan(end_file[i_tr]):
        #                 start_idx = int(start_file[i_tr]) if not np.isnan(start_file[i_tr]) else 0
        #                 end_idx = int(end_file[i_tr]) if not np.isnan(end_file[i_tr]) else len(spikes)
        #                 s = spikes[start_idx:end_idx].astype(np.float32)  # Convert to float32
        #                 s = np.convolve(s, np.ones(smooth_window_frames) / smooth_window_frames, mode='same')
        #                 time = np.arange(1, len(s) + 1) / frame_rate + fr_interval[0]
        #                 s_resampled = np.interp(time_new, time, s)
        #                 psth_all.append(s_resampled)

        # time = time_new



        idx_regular = np.array(idx_regular)
        #psth_all = np.array(psth_all)
        if psth_all:
            psth_regular_idx = [psth_all[idx] for idx in idx_regular]
            psth_odd_regular = [psth_all[idx] for idx in idx_odd_regular]
            psth_even_regular = [psth_all[idx] for idx in idx_even_regular]
                # # Remove None values from the list
                # psth_regular_filtered = [sublist for sublist in psth_regular_idx if sublist is not None]
                # # Convert the list of sublists to a 1D numpy array
                # psth_regular_array = np.concatenate(psth_regular_filtered)
                # # Calculate the mean
                # psth_regular = np.mean(psth_regular_array)
            psth_regular_stacked = np.vstack([sublist for sublist in psth_regular_idx if sublist is not None])
            psth_regular = np.mean(psth_regular_stacked, axis=0)
            #psth_regular = np.mean(np.concatenate([sublist.flatten() for sublist in psth_regular_idx if sublist is not None]))
            psth_regular_stem = np.std(np.vstack([sublist for sublist in psth_regular_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_regular))
            psth_regular_odd = np.mean(np.vstack([sublist for sublist in psth_odd_regular if sublist is not None]), axis=0)
            psth_regular_even = np.mean(np.vstack([sublist for sublist in psth_even_regular if sublist is not None]), axis=0)
            #psth_regular_odd = np.nanmean(np.concatenate([sublist.flatten() for sublist in psth_odd_regular if sublist is not None]))
            #psth_regular_even = np.nanmean(np.concatenate([sublist.flatten() for sublist in psth_even_regular if sublist is not None]))
            # psth_regular = np.mean(np.concatenate([sublist for sublist in psth_regular_idx if sublist is not None]))
            # #psth_regular = np.mean(np.stack(psth_regular, axis=0), axis=0)
            # #psth_regular = np.mean(np.vstack[psth_regular_idx], axis=0)
            # psth_regular_stem = np.std(np.concatenate([sublist for sublist in psth_regular_idx if sublist is not None])) / np.sqrt(len(idx_regular))
            # psth_regular_odd = np.nanmean(np.concatenate([sublist for sublist in psth_odd_regular if sublist is not None]), axis=0)
            # psth_regular_even = np.nanmean(np.concatenate([sublist for sublist in psth_even_regular if sublist is not None]), axis=0)
            #psth_regular_even = np.nanmean(np.vstack(psth_all[idx_even_regular]), axis=0)
            # psth_regular1={i: value for i, value in enumerate(psth_regular)}
            # psth_regular_stem1= {i: value for i, value in enumerate(psth_regular_stem)}
            # psth_regular_odd1={i: value for i, value in enumerate(psth_regular_odd)}
            # psth_regular_even1={i: value for i, value in enumerate(psth_regular_even)}
            # time1={i: value for i, value in enumerate(time)}
            psth_regular1=np.array([psth_regular], dtype=np.float32)
            psth_regular_stem1=np.array([psth_regular_stem], dtype=np.float32)
            psth_regular_odd1=np.array([psth_regular_odd], dtype=np.float32)
            psth_regular_even1=np.array([psth_regular_even], dtype=np.float32)
            time1=np.array([time], dtype=np.float32)

            key_ROI1[i_roi]['psth_regular'] = psth_regular1
            key_ROI1[i_roi]['psth_regular_stem'] = psth_regular_stem1
            key_ROI1[i_roi]['psth_regular_odd'] = psth_regular_odd1
            key_ROI1[i_roi]['psth_regular_even'] = psth_regular_even1
            key_ROI1[i_roi]['psth_time'] = time1

                # Calculating Pearson correlation for odd vs even to see if the data matches itself
            r = np.corrcoef(psth_regular_odd, psth_regular_even, rowvar=False)
            #r = np.corrcoef([psth_regular_odd.flatten(), psth_regular_even.flatten()], rowvar=False)
            key_ROI2[i_roi]['psth_regular_odd_vs_even_corr'] = r[0, 1]

                # Identifying the peak in the trace and when it occurred for the whole data
            idx_peak = np.argmax(psth_regular)
            key_ROI2[i_roi]['peaktime_psth_regular'] = time[idx_peak]

            idx_peak = np.argmax(psth_regular_odd)
            key_ROI2[i_roi]['peaktime_psth_regular_odd'] = time[idx_peak]

            idx_peak = np.argmax(psth_regular_even)
            key_ROI2[i_roi]['peaktime_psth_regular_even'] = time[idx_peak]


                # key_ROI1[i_roi].insert1({
                #     'psth_regular': psth_regular,
                #     'psth_regular_stem': psth_regular_stem,
                #     'psth_regular_odd': psth_regular_odd,
                #     'psth_regular_even': psth_regular_even,
                #     'psth_time': time
                # })

                # # Calculating Pearson correlation for odd vs even to see if the data matches itself
                # r = np.corrcoef(psth_regular_odd, psth_regular_even)[0, 1]
                # key_ROI2[i_roi].insert1({'psth_regular_odd_vs_even_corr': r})

                # # Identifying the peak in the trace and when it occurred for the whole data
                # idx_peak = np.argmax(psth_regular)
                # key_ROI2[i_roi].insert1({'peaktime_psth_regular': time[idx_peak]})

                # idx_peak = np.argmax(psth_regular_odd)
                # key_ROI2[i_roi].insert1({'peaktime_psth_regular_odd': time[idx_peak]})

                # idx_peak = np.argmax(psth_regular_even)
                # key_ROI2[i_roi].insert1({'peaktime_psth_regular_even': time[idx_peak]})
            # example for later
            # psth_regular_idx = [psth_all[idx] for idx in idx_regular]
            # psth_odd_regular = [psth_all[idx] for idx in idx_odd_regular]
            # psth_even_regular = [psth_all[idx] for idx in idx_even_regular]

            # psth_regular_stacked = np.vstack([sublist for sublist in psth_regular_idx if sublist is not None])
            # psth_regular = np.mean(psth_regular_stacked, axis=0)

            #try:
                # Taking the mean PSTH across trials
            psth_small_idx = [psth_all[idx] for idx in idx_small]
            psth_odd_small = [psth_all[idx] for idx in idx_odd_small]
            psth_even_small = [psth_all[idx] for idx in idx_even_small]

            psth_small_stacked = np.vstack([sublist for sublist in psth_small_idx if sublist is not None])
            psth_small = np.mean(psth_small_stacked, axis=0)
            psth_small_stem = np.std(np.vstack([sublist for sublist in psth_small_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_small))
            psth_small_odd = np.mean(np.vstack([sublist for sublist in psth_odd_small if sublist is not None]), axis=0)
            psth_small_even = np.mean(np.vstack([sublist for sublist in psth_even_small if sublist is not None]), axis=0)

            #psth_small = np.nanmean(psth_all[idx_small], axis=0)
            # psth_small_stem = np.std(psth_all[idx_small], axis=0) / np.sqrt(len(idx_small))
            # psth_small_odd = np.nanmean(psth_all[idx_odd_small], axis=0)
            # psth_small_even = np.nanmean(psth_all[idx_even_small], axis=0)

            psth_large_idx = [psth_all[idx] for idx in idx_large]
            psth_odd_large = [psth_all[idx] for idx in idx_odd_large]
            psth_even_large = [psth_all[idx] for idx in idx_even_large]

            psth_large_stacked = np.vstack([sublist for sublist in psth_large_idx if sublist is not None])
            psth_large = np.mean(psth_large_stacked, axis=0)
            psth_large_stem = np.std(np.vstack([sublist for sublist in psth_large_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_large))
            psth_large_odd = np.mean(np.vstack([sublist for sublist in psth_odd_large if sublist is not None]), axis=0)
            psth_large_even = np.mean(np.vstack([sublist for sublist in psth_even_large if sublist is not None]), axis=0)
            
            # psth_large = np.nanmean(psth_all[idx_large], axis=0)
            # psth_large_stem = np.std(psth_all[idx_large], axis=0) / np.sqrt(len(idx_large))
            # psth_large_odd = np.nanmean(psth_all[idx_odd_large], axis=0)
            # psth_large_even = np.nanmean(psth_all[idx_even_large], axis=0)
            # psth_small={i: value for i, value in enumerate(psth_small)}
            # psth_small_stem={i: value for i, value in enumerate(psth_small_stem)}
            # psth_small_odd={i: value for i, value in enumerate(psth_small_odd)}
            # psth_small_even={i: value for i, value in enumerate(psth_small_even)}
            psth_large1=np.array([psth_large], dtype=np.float32)
            psth_large_stem1=np.array([psth_large_stem], dtype=np.float32)
            psth_large_odd1=np.array([psth_large_odd], dtype=np.float32)
            psth_large_even1=np.array([psth_large_even], dtype=np.float32)
            psth_small1=np.array([psth_small], dtype=np.float32)
            psth_small_stem1=np.array([psth_small_stem], dtype=np.float32)
            psth_small_odd1=np.array([psth_small_odd], dtype=np.float32)
            psth_small_even1=np.array([psth_small_even], dtype=np.float32)

            key_ROI1[i_roi]['psth_small'] = psth_small1
            key_ROI1[i_roi]['psth_small_stem'] = psth_small_stem1
            key_ROI1[i_roi]['psth_small_odd'] = psth_small_odd1
            key_ROI1[i_roi]['psth_small_even'] = psth_small_even1

            key_ROI1[i_roi]['psth_large'] = psth_large1
            key_ROI1[i_roi]['psth_large_stem'] = psth_large_stem1
            key_ROI1[i_roi]['psth_large_odd'] = psth_large_odd1
            key_ROI1[i_roi]['psth_large_even'] = psth_large_even1

            # key_ROI1[i_roi].psth_small = psth_small
            # key_ROI1[i_roi].psth_small_stem = psth_small_stem
            # key_ROI1[i_roi].psth_small_odd = psth_small_odd
            # key_ROI1[i_roi].psth_small_even = psth_small_even
            
            # key_ROI1[i_roi].psth_large = psth_large
            # key_ROI1[i_roi].psth_large_stem = psth_large_stem
            # key_ROI1[i_roi].psth_large_odd = psth_large_odd
            # key_ROI1[i_roi].psth_large_even = psth_large_even

            r = np.corrcoef(psth_small_odd, psth_small_even, rowvar=False)
            key_ROI2[i_roi]['psth_small_odd_vs_even_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_large_odd, psth_large_even, rowvar=False)
            key_ROI2[i_roi]['psth_large_odd_vs_even_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_regular, psth_small, rowvar=False)
            key_ROI2[i_roi]['psth_regular_vs_small_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_regular, psth_large, rowvar=False)
            key_ROI2[i_roi]['psth_regular_vs_large_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_small, psth_large, rowvar=False)
            key_ROI2[i_roi]['psth_small_vs_large_corr'] = r[0, 1]
            
            #idx_peak = np.argmax(psth_regular)
            #key_ROI2[i_roi]['peaktime_psth_regular'] = time[idx_peak]

            idx_peak_small = np.argmax(psth_small)
            key_ROI2[i_roi]['peaktime_psth_small'] = time[idx_peak_small]
            
            idx_peak_regular = np.argmax(psth_regular)
            key_ROI2[i_roi]['peaktime_psth_regular'] = time[idx_peak_regular]
            
            idx_peak_large = np.argmax(psth_large)
            key_ROI2[i_roi]['peaktime_psth_large'] = time[idx_peak_large]
            
            # Single trials, averaged across all time duration in a specific time interval
            idx_onset = (time >= fr_interval_limit[0]) & (time < fr_interval_limit[1])
            
            temp_regular = []
            for idx in idx_regular:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_regular.append(sublist_array[idx_onset])

            psth_regular_trials = []
            for sublist in temp_regular:
                mean_value = np.nanmean(sublist)
                psth_regular_trials.append(mean_value)

            temp_small = []
            for idx in idx_small:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_small.append(sublist_array[idx_onset])

            psth_small_trials = []
            for sublist in temp_small:
                mean_value = np.nanmean(sublist)
                psth_small_trials.append(mean_value)

            temp_large = []
            for idx in idx_large:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_large.append(sublist_array[idx_onset])

            psth_large_trials = []
            for sublist in temp_large:
                mean_value = np.nanmean(sublist)
                psth_large_trials.append(mean_value)
                        
            # temp = psth_all[idx_regular][:, idx_onset]
            # psth_regular_trials = np.nanmean(temp, axis=1)
            
            # temp = psth_all[idx_small][:, idx_onset]
            # psth_small_trials = np.nanmean(temp, axis=1)
            
            # temp = psth_all[idx_large][:, idx_onset]
            # psth_large_trials = np.nanmean(temp, axis=1)
            
            p_val_regular_small = ranksums(psth_regular_trials, psth_small_trials)
            p_val_regular_small = p_val_regular_small.pvalue
            key_ROI2[i_roi]['reward_mean_pval_regular_small'] = p_val_regular_small
            
            p_val_regular_large = ranksums(psth_regular_trials, psth_large_trials)
            p_val_regular_large = p_val_regular_large.pvalue
            key_ROI2[i_roi]['reward_mean_pval_regular_large'] = p_val_regular_large
            
            p_val_small_large = ranksums(psth_small_trials, psth_large_trials)
            p_val_small_large = p_val_small_large.pvalue
            key_ROI2[i_roi]['reward_mean_pval_small_large'] = p_val_small_large
            
            key_ROI2[i_roi]['reward_mean_regular'] = np.nanmean(psth_regular_trials)
            key_ROI2[i_roi]['reward_mean_small'] = np.nanmean(psth_small_trials)
            key_ROI2[i_roi]['reward_mean_large'] = np.nanmean(psth_large_trials)    

            # At peak response time

            psth_regular_trials_peak = []
            for idx in idx_regular:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    sublist_reshaped = sublist_array.reshape(1, -1)  # Reshape to 2D array
                    sublist_peak = sublist_reshaped[:, idx_peak_regular]
                    psth_regular_trials_peak.append(sublist_peak)

            psth_small_trials_peak = []
            for idx in idx_small:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    sublist_reshaped = sublist_array.reshape(1, -1)  # Reshape to 2D array
                    sublist_peak = sublist_reshaped[:, idx_peak_small]
                    psth_small_trials_peak.append(sublist_peak)

            psth_large_trials_peak = []
            for idx in idx_large:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    sublist_reshaped = sublist_array.reshape(1, -1)  # Reshape to 2D array
                    sublist_peak = sublist_reshaped[:, idx_peak_large]
                    psth_large_trials_peak.append(sublist_peak)

            # psth_regular_trials_peak = psth_all[idx_regular][:, idx_peak_regular]
            # psth_small_trials_peak = psth_all[idx_small][:, idx_peak_small]
            # psth_large_trials_peak = psth_all[idx_large][:, idx_peak_large]
                    
            key_ROI2[i_roi]['reward_peak_regular'] = np.nanmean(psth_regular_trials_peak)
            key_ROI2[i_roi]['reward_peak_small'] = np.nanmean(psth_small_trials_peak)
            key_ROI2[i_roi]['reward_peak_large'] = np.nanmean(psth_large_trials_peak)
            
            p_val_regular_small_peak = ranksums(psth_regular_trials_peak, psth_small_trials_peak)
            p_val_regular_small_peak= p_val_regular_small_peak.pvalue
            key_ROI2[i_roi]['reward_peak_pval_regular_small'] = float(p_val_regular_small_peak)
            
            p_val_regular_large_peak = ranksums(psth_regular_trials_peak, psth_large_trials_peak)
            p_val_regular_large_peak = p_val_regular_large_peak.pvalue
            key_ROI2[i_roi]['reward_peak_pval_regular_large'] = float(p_val_regular_large_peak)
            
            _, p_val_small_large_peak = ranksums(psth_small_trials_peak, psth_large_trials_peak)
            #p_val_small_large_peak = p_val_regular_large_peak.pvalue  ##########error#####
            if p_val_small_large_peak:
                key_ROI2[i_roi]['reward_peak_pval_small_large'] = float(p_val_small_large_peak)
                
            #except:
            #    pass

            #try:
                # Taking the mean PSTH across trials
                # example

            # psth_small_stacked = np.vstack([sublist for sublist in psth_small_idx if sublist is not None])
            # psth_small = np.mean(psth_small_stacked, axis=0)
            # psth_small_stem = np.std(np.vstack([sublist for sublist in psth_small_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_small))
            # psth_small_odd = np.mean(np.vstack([sublist for sublist in psth_odd_small if sublist is not None]), axis=0)
            # psth_small_even = np.mean(np.vstack([sublist for sublist in psth_even_small if sublist is not None]), axis=0)
            psth_first_idx = [psth_all[idx] for idx in idx_first] #good
            psth_first_odd = [psth_all[idx] for idx in idx_odd_first]
            psth_first_even = [psth_all[idx] for idx in idx_even_first]
            
            psth_begin_idx = [psth_all[idx] for idx in idx_begin]
            psth_begin_odd = [psth_all[idx] for idx in idx_odd_begin]
            psth_begin_even = [psth_all[idx] for idx in idx_even_begin]
            
            psth_mid_idx = [psth_all[idx] for idx in idx_mid]
            psth_mid_odd = [psth_all[idx] for idx in idx_odd_mid]
            psth_mid_even = [psth_all[idx] for idx in idx_even_mid]

            psth_end_idx = [psth_all[idx] for idx in idx_end]
            psth_end_odd = [psth_all[idx] for idx in idx_odd_end]
            psth_end_even = [psth_all[idx] for idx in idx_even_end]

            psth_first_stacked = np.vstack([sublist for sublist in psth_first_idx if sublist is not None])#good
            psth_first = np.nanmean(psth_first_stacked, axis=0)#good
            psth_first_stem = np.std(np.vstack([sublist for sublist in psth_first_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_first))#good
            psth_first_odd = np.nanmean(psth_first_odd, axis=0)#
            psth_first_even = np.nanmean(psth_first_even, axis=0)#

            psth_begin_stacked = np.vstack([sublist for sublist in psth_begin_idx if sublist is not None])#good
            psth_begin = np.nanmean(psth_begin_stacked, axis=0)#good
            psth_begin_stem = np.std(np.vstack([sublist for sublist in psth_begin_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_begin))#good
            psth_begin_odd = np.nanmean(psth_begin_odd, axis=0)#
            psth_begin_even = np.nanmean(psth_begin_even, axis=0)#

            psth_mid_stacked = np.vstack([sublist for sublist in psth_mid_idx if sublist is not None])#good
            psth_mid = np.nanmean(psth_mid_stacked, axis=0)#good
            psth_mid_stem = np.std(np.vstack([sublist for sublist in psth_mid_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_mid))#good
            psth_mid_odd = np.nanmean(psth_mid_odd, axis=0)#
            psth_mid_even = np.nanmean(psth_mid_even, axis=0)#
            
            psth_end_stacked = np.vstack([sublist for sublist in psth_end_idx if sublist is not None])#good
            psth_end = np.nanmean(psth_end_stacked, axis=0)#good
            psth_end_stem = np.std(np.vstack([sublist for sublist in psth_end_idx if sublist is not None]), axis=0) / np.sqrt(len(idx_end))#good
            psth_end_odd = np.nanmean(psth_end_odd, axis=0)#
            psth_end_even = np.nanmean(psth_end_even, axis=0)#

            psth_first1=np.array([psth_first], dtype=np.float32)
            psth_first_stem1=np.array([psth_first_stem], dtype=np.float32)
            psth_first_odd1=np.array([psth_first_odd], dtype=np.float32)
            psth_first_even1=np.array([psth_first_even], dtype=np.float32)
            psth_begin1=np.array([psth_begin], dtype=np.float32)
            psth_begin_stem1=np.array([psth_begin_stem], dtype=np.float32)
            psth_begin_odd1=np.array([psth_begin_odd], dtype=np.float32)
            psth_begin_even1=np.array([psth_begin_even], dtype=np.float32)
            psth_mid1=np.array([psth_mid], dtype=np.float32)
            psth_mid_stem1=np.array([psth_mid_stem], dtype=np.float32)
            psth_mid_odd1=np.array([psth_mid_odd], dtype=np.float32)
            psth_mid_even1=np.array([psth_mid_even], dtype=np.float32)
            psth_end1=np.array([psth_end], dtype=np.float32)
            psth_end_stem1=np.array([psth_end_stem], dtype=np.float32)
            psth_end_odd1=np.array([psth_end_odd], dtype=np.float32)
            psth_end_even1=np.array([psth_end_even], dtype=np.float32)


            key_ROI3[i_roi]['psth_first'] = psth_first1
            key_ROI3[i_roi]['psth_first_stem'] = psth_first_stem1
            key_ROI3[i_roi]['psth_first_odd'] = psth_first_odd1
            key_ROI3[i_roi]['psth_first_even'] = psth_first_even1
            
            key_ROI3[i_roi]['psth_begin'] = psth_begin1
            key_ROI3[i_roi]['psth_begin_stem'] = psth_begin_stem1
            key_ROI3[i_roi]['psth_begin_odd'] = psth_begin_odd1
            key_ROI3[i_roi]['psth_begin_even'] = psth_begin_even1
            
            key_ROI3[i_roi]['psth_mid'] = psth_mid1
            key_ROI3[i_roi]['psth_mid_stem'] = psth_mid_stem1
            key_ROI3[i_roi]['psth_mid_odd'] = psth_mid_odd1
            key_ROI3[i_roi]['psth_mid_even'] = psth_mid_even1
            
            key_ROI3[i_roi]['psth_end'] = psth_end1#
            key_ROI3[i_roi]['psth_end_stem'] = psth_end_stem1#
            key_ROI3[i_roi]['psth_end_odd'] = psth_end_odd1#
            key_ROI3[i_roi]['psth_end_even'] = psth_end_even1#
            

            #example
            #r = np.corrcoef(psth_regular_odd, psth_regular_even, rowvar=False)
            # #r = np.corrcoef([psth_regular_odd.flatten(), psth_regular_even.flatten()], rowvar=False)
            # key_ROI2[i_roi]['psth_regular_odd_vs_even_corr'] = r[0, 1]


            # Stability
            r = np.corrcoef(psth_first_odd, psth_first_even, rowvar=False)
            key_ROI4[i_roi]['psth_first_odd_vs_even_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_begin_odd, psth_begin_even, rowvar=False)
            key_ROI4[i_roi]['psth_begin_odd_vs_even_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_mid_odd, psth_mid_even, rowvar=False)
            key_ROI4[i_roi]['psth_mid_odd_vs_even_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_end_odd, psth_end_even, rowvar=False)
            key_ROI4[i_roi]['psth_end_odd_vs_even_corr'] = r[0, 1]
            
            # Between conditions
            r = np.corrcoef(psth_first, psth_begin, rowvar=False)
            key_ROI4[i_roi]['psth_first_vs_begin_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_first, psth_mid, rowvar=False)
            key_ROI4[i_roi]['psth_first_vs_mid_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_first, psth_end, rowvar=False)
            key_ROI4[i_roi]['psth_first_vs_end_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_begin, psth_end, rowvar=False)
            key_ROI4[i_roi]['psth_begin_vs_end_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_begin, psth_mid, rowvar=False)
            key_ROI4[i_roi]['psth_begin_vs_mid_corr'] = r[0, 1]
            
            r = np.corrcoef(psth_mid, psth_end, rowvar=False)
            key_ROI4[i_roi]['psth_mid_vs_end_corr'] = r[0, 1]
            
            #     # Identifying the peak in the trace and when it occurred for the whole data
            # idx_peak = np.argmax(psth_regular)
            # key_ROI2[i_roi]['peaktime_psth_regular'] = time[idx_peak]

            idx_peak_first = np.argmax(psth_first)
            key_ROI4[i_roi]['peaktime_psth_first'] = time[idx_peak_first]
            idx_peak_begin = np.argmax(psth_begin)
            key_ROI4[i_roi]['peaktime_psth_begin'] = time[idx_peak_begin]
            idx_peak_mid = np.argmax(psth_mid)
            key_ROI4[i_roi]['peaktime_psth_mid'] = time[idx_peak_mid]
            idx_peak_end = np.argmax(psth_end)
            key_ROI4[i_roi]['peaktime_psth_end'] = time[idx_peak_end]

            # temp_regular = []
            # for idx in idx_regular:
            #     sublist = psth_all[idx]
            #     if sublist is not None:
            #         sublist_array = np.array(sublist)
            #         temp_regular.append(sublist_array[idx_onset])

            # psth_regular_trials = []
            # for sublist in temp_regular:
            #     mean_value = np.nanmean(sublist)
            #     psth_regular_trials.append(mean_value)

            # Single trials, averaged across all time duration in a specific time interval (e.g., after the licport onset (t>=0))
            temp_first = []
            for idx in idx_first:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_first.append(sublist_array[idx_onset])

            psth_first_trials = []
            for sublist in temp_first:
                mean_value = np.nanmean(sublist)
                psth_first_trials.append(mean_value)

            temp_begin = []
            for idx in idx_begin:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_begin.append(sublist_array[idx_onset])

            psth_begin_trials = []
            for sublist in temp_begin:
                mean_value = np.nanmean(sublist)
                psth_begin_trials.append(mean_value)

            temp_mid = []
            for idx in idx_mid:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_mid.append(sublist_array[idx_onset])

            psth_mid_trials = []
            for sublist in temp_mid:
                mean_value = np.nanmean(sublist)
                psth_mid_trials.append(mean_value)

            temp_end = []
            for idx in idx_end:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_end.append(sublist_array[idx_onset])

            psth_end_trials = []
            for sublist in temp_end:
                mean_value = np.nanmean(sublist)
                psth_end_trials.append(mean_value)

            # idx_onset = (time >= fr_interval_limit[0]) & (time < fr_interval_limit[1])
            # temp = np.array(psth_all[idx_first])
            # psth_first_trials = np.nanmean(temp[:, idx_onset], axis=1)
            # temp = np.array(psth_all[idx_begin])
            # psth_begin_trials = np.nanmean(temp[:, idx_onset], axis=1)
            # temp = np.array(psth_all[idx_mid])
            # psth_mid_trials = np.nanmean(temp[:, idx_onset], axis=1)
            # temp = np.array(psth_all[idx_end])
            # psth_end_trials = np.nanmean(temp[:, idx_onset], axis=1)
            
            key_ROI4[i_roi]['block_mean_first'] = np.nanmean(psth_first_trials)
            key_ROI4[i_roi]['block_mean_begin'] = np.nanmean(psth_begin_trials)
            key_ROI4[i_roi]['block_mean_mid'] = np.nanmean(psth_mid_trials)
            key_ROI4[i_roi]['block_mean_end'] = np.nanmean(psth_end_trials)
                        
            _, p = ranksums(psth_first_trials, psth_begin_trials)
            key_ROI4[i_roi]['block_mean_pval_first_begin'] = float(p)
            _, p = ranksums(psth_first_trials, psth_end_trials)
            key_ROI4[i_roi]['block_mean_pval_first_end'] = float(p)
            _, p = ranksums(psth_begin_trials, psth_end_trials)
            key_ROI4[i_roi]['block_mean_pval_begin_end'] = float(p)
            
            #example
            temp_first = []
            for idx in idx_first:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_first.append(sublist_array[idx_peak_first])

            psth_first_trials_peak = []
            for sublist in temp_first:
                mean_value = np.nanmean(sublist)
                psth_first_trials_peak.append(mean_value)

            temp_begin = []
            for idx in idx_begin:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_begin.append(sublist_array[idx_peak_begin])

            psth_begin_trials_peak = []
            for sublist in temp_begin:
                mean_value = np.nanmean(sublist)
                psth_begin_trials_peak.append(mean_value)

            temp_mid = []
            for idx in idx_mid:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_mid.append(sublist_array[idx_peak_mid])

            psth_mid_trials_peak = []
            for sublist in temp_mid:
                mean_value = np.nanmean(sublist)
                psth_mid_trials_peak.append(mean_value)

            temp_end = []
            for idx in idx_end:
                sublist = psth_all[idx]
                if sublist is not None:
                    sublist_array = np.array(sublist)
                    temp_end.append(sublist_array[idx_peak_end])

            psth_end_trials_peak = []
            for sublist in temp_end:
                mean_value = np.nanmean(sublist)
                psth_end_trials_peak.append(mean_value)
            # ##


            # At peak response time
            # temp1 = [psth_all[int(idx)] for idx in idx_first] #works
            # temp = np.array(psth_all[idx_first])##error###
            # psth_first_trials_peak = temp[:, idx_peak_first]
            # temp = np.array(psth_all[idx_begin])
            # psth_begin_trials_peak = temp[:, idx_peak_begin]
            # temp = np.array(psth_all[idx_mid])
            # psth_mid_trials_peak = temp[:, idx_peak_mid]
            # temp = np.array(psth_all[idx_end])
            # psth_end_trials_peak = temp[:, idx_peak_end]
            
            key_ROI4[i_roi]['block_peak_first'] = np.nanmean(psth_first_trials_peak)
            key_ROI4[i_roi]['block_peak_begin'] = np.nanmean(psth_begin_trials_peak)
            key_ROI4[i_roi]['block_peak_mid'] = np.nanmean(psth_mid_trials_peak)
            key_ROI4[i_roi]['block_peak_end'] = np.nanmean(psth_end_trials_peak)
            
            _, p = ranksums(psth_first_trials_peak, psth_begin_trials_peak)
            key_ROI4[i_roi]['block_peak_pval_first_begin'] = float(p)
            _, p = ranksums(psth_first_trials_peak, psth_end_trials_peak)
            key_ROI4[i_roi]['block_peak_pval_first_end'] = float(p)
            _, p = ranksums(psth_begin_trials_peak, psth_end_trials_peak)
            key_ROI4[i_roi]['block_peak_pval_begin_end'] = float(p)
                
            # insert(self4, k2)
        #except:
        #    pass

        #else:
        #    pass# decide what to do and change the pass accordingly
        # Handle the case when the restrictions result in empty arrays

      #try_key_ROI1 = [(d['subject_id'], d['session'], d['fov_num'], d['plane_num'], d['channel_num'], d['roi_number'], d['session_epoch_type'], d['session_epoch_number'], d['psth_regular'], d['psth_regular_stem'], d['psth_regular_odd'], d['psth_regular_even'], d['psth_time'], d['psth_small'], d['psth_small_stem'], d['psth_small_odd'], d['psth_small_even'], d['psth_large'], d['psth_large_stem'], d['psth_large_odd'], d['psth_large_even']) for d in key_ROI1]
      # Inserting bulk data into tables
      
    self.insert(key_ROI1, skip_duplicates=True, allow_direct_insert=True)
    self2.insert(key_ROI2, skip_duplicates=True, allow_direct_insert=True)  

    #try:
        # Insert into key_ROI3 table
    self3.insert(key_ROI3, skip_duplicates=True, allow_direct_insert=True) 
    #except:
    #   pass

    #try:
    # Insert into key_ROI4 table
    self4.insert(key_ROI4, skip_duplicates=True, allow_direct_insert=True)  
    #except:
    #    pass

    #         #start_file[-1] = float('nan')
    #         #end_file[-1] = float('nan')
    #         #start_file[-1], end_file[-1] = np.nan, np.nan  # we don't use the very last trial

