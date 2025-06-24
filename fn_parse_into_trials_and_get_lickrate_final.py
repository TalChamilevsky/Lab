def fn_parse_into_trials_and_get_lickrate1 (key, frame_rate, time_bin, flag_electric_video):

    import datajoint as dj
    import numpy as np
    from datajoint import fetch
    img= dj.schema('arseny_learning_imaging')
    img= dj.VirtualModule('IMG', 'arseny_learning_imaging')
    tracking= dj.schema('arseny_learning_tracking')
    tracking= dj.VirtualModule('TRACKING', 'arseny_learning_tracking')
    exp2= dj.schema('arseny_s1alm_experiment2')
    exp2= dj.VirtualModule ('EXP2', 'arseny_s1alm_experiment2')
   # key = {'key': ''}  # specify the key 

    import decimal

    TrialsStartFrame = ((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch('session_epoch_trial_start_frame', order_by='trial')
    trial_num = ((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch('trial', order_by='trial')

    if len(TrialsStartFrame) == 0:
        TrialsStartFrame = (img.FrameStartFile & key).fetch('session_epoch_file_start_frame', order_by='session_epoch_file_num')
        trial_num = ((exp2.BehaviorTrial & key) - tracking.VideoGroomingTrial).fetch('trial', order_by='trial')
        TrialsStartFrame = TrialsStartFrame[trial_num]

    if flag_electric_video == 1:
        LICK_VIDEO = []  # We align based on electric lickport, even if video does not exist
    elif flag_electric_video == 2:
        # We align based on video if it exists
        # We align to the first video-detected lick after lickport movement
        LICK_VIDEO = ((tracking.VideoNthLickTrial & key) - tracking.VideoGroomingTrial).fetch('lick_time_onset_relative_to_trial_start')

    go_time = (((exp2.BehaviorTrial.Event & key) - tracking.VideoGroomingTrial) & 'trial_event_type="go"').fetch('trial_event_time')
    LICK_ELECTRIC = ((exp2.ActionEvent & key) - tracking.VideoGroomingTrial).fetch()

    start_file = np.zeros(len(trial_num))
    end_file = np.zeros(len(trial_num))
    lick_tr_times_relative_to_first_lick_after_go = []
    lick_tr_total = []
    
    for i_tr in range(len(trial_num)):
        if len(LICK_VIDEO) > 0:
            all_licks = LICK_VIDEO[LICK_VIDEO['trial'] == trial_num[i_tr]]['lick_time_onset_relative_to_trial_start']
            licks_after_go = all_licks[all_licks > go_time[i_tr]]
        else:
            all_licks = LICK_ELECTRIC[LICK_ELECTRIC['trial'] == trial_num[i_tr]]['action_event_time']
            licks_after_go = all_licks[all_licks > go_time[i_tr]]
        
        if len(licks_after_go) > 0:
            start_file[i_tr] = TrialsStartFrame[i_tr] + int(float(licks_after_go[0]) * frame_rate) + int(time_bin[0] * frame_rate)
            end_file[i_tr] = start_file[i_tr] + int(float(time_bin[1] - time_bin[0]) * frame_rate) - 1
            
            lick_tr_times_relative_to_first_lick_after_go.append(all_licks - licks_after_go[0])
            lick_tr_total.append(np.sum((lick_tr_times_relative_to_first_lick_after_go[i_tr] >= float(time_bin[0])) & (lick_tr_times_relative_to_first_lick_after_go[i_tr] <= float(time_bin[-1]))))
            
            if start_file[i_tr] <= 0:
                start_file[i_tr] = float('nan')
                end_file[i_tr] = float('nan')

        else:
            start_file[i_tr] = float('nan')
            end_file[i_tr] = float('nan')
            lick_tr_total.append(0)
            lick_tr_times_relative_to_first_lick_after_go.append([])

    

    # lick_tr_times_relative_to_first_lick_after_go = []
    # lick_tr_total = []

    # for i_tr in range(len(trial_num)):
    #     if len(LICK_VIDEO) != 0:
    #         all_licks = [lick['lick_time_onset_relative_to_trial_start'] for lick in LICK_VIDEO if lick['trial'] == trial_num[i_tr]]
    #         licks_after_go = [lick for lick in all_licks if lick > go_time[i_tr]]
    #     else:
    #         all_licks = [lick['action_event_time'] for lick in LICK_ELECTRIC if lick['trial'] == trial_num[i_tr]]
    #         licks_after_go = [lick for lick in all_licks if lick > go_time[i_tr]]

    #     if len(licks_after_go) != 0:
    #         start_file.append(TrialsStartFrame[i_tr] + int(licks_after_go[0] * frame_rate) + int(float(time_bin[0]) * frame_rate))
    #         end_file.append(start_file[-1] + int((time_bin[1] - time_bin[0]) * frame_rate) - 1)
            
    #         lick_tr_times_relative_to_first_lick_after_go.append([lick - licks_after_go[0] for lick in all_licks])
    #         lick_tr_total.append(sum([1 for lick in lick_tr_times_relative_to_first_lick_after_go[-1] if lick >= time_bin[0] and lick <= time_bin[-1]]))
            
    #         if start_file <= 0:
    #             start_file = float('nan')
    #             end_file = float('nan')
    #     else:
    #         start_file = float('nan')
    #         end_file = float('nan')
    #         lick_tr_total.append(0)
    #         lick_tr_times_relative_to_first_lick_after_go.append([])

    return start_file, end_file, lick_tr_times_relative_to_first_lick_after_go, lick_tr_total

    #     TrialsStartFrame = (img.FrameStartTrial & key).fetch('session_epoch_trial_start_frame', order_by='trial')
    #     trial_num = (img.FrameStartTrial & key).fetch('trial', order_by='trial')

    #     if len(TrialsStartFrame) == 0:
    #         TrialsStartFrame = (img.FrameStartFile & key).fetch('session_epoch_file_start_frame', order_by='session_epoch_file_num')
    #         trial_num = (exp2.BehaviorTrial & key).fetch('trial', order_by='trial')
    #         TrialsStartFrame = TrialsStartFrame[trial_num]

    #     if flag_electric_video == 1:
    #         LICK_VIDEO = []  # We align based on electric lickport, even if video does exist
    #     elif flag_electric_video == 2:
    #         LICK_VIDEO = (tracking.VideoNthLickTrial & key).fetch('lick_time_onset_relative_to_trial_start')  # video-based lick detection

    #     go_time = (exp2.BehaviorTrial.Event & key & 'trial_event_type="go"').fetch('trial_event_time')
    #     LICK_ELECTRIC = (exp2.ActionEvent & key).fetch()

    #     lick_tr_times_relative_to_first_lick_after_go = []
    #     lick_tr_total = []

    #     for i_tr in range(len(trial_num)):
    #         if len(LICK_VIDEO) > 0:
    #             all_licks = LICK_VIDEO[np.where(LICK_VIDEO['trial'] == trial_num[i_tr])]['lick_time_onset_relative_to_trial_start']
    #             #all_licks = (LICK_VIDEO & {'trial': trial_num[i_tr]}).fetch('lick_time_onset_relative_to_trial_start')
    #             #all_licks = LICK_VIDEO[LICK_VIDEO['trial'] == trial_num[i_tr]]['lick_time_onset_relative_to_trial_start']
    #             licks_after_go = all_licks[all_licks > float(go_time[i_tr])]
    #         else:
    #             all_licks = LICK_ELECTRIC[np.where(LICK_ELECTRIC['trial'] == trial_num[i_tr])]['action_event_time']
    #             licks_after_go = all_licks[all_licks > float(go_time[i_tr])]

    #         if len(licks_after_go) > 0:
    #             start_file = int(TrialsStartFrame[i_tr]) + int(float(licks_after_go[0]) * float(frame_rate)) + int(float(time_bin[0]) * float(frame_rate))
    #             end_file = start_file + int((float(time_bin[1]) - float(time_bin[0])) * float(frame_rate)) - 1

    #             lick_tr_times_relative_to_first_lick_after_go.append(all_licks - licks_after_go[0])
    #             lick_tr_total.append(
    #                 np.sum((lick_tr_times_relative_to_first_lick_after_go[i_tr] >= float(time_bin[0])) &
    #                        (lick_tr_times_relative_to_first_lick_after_go[i_tr] <= float(time_bin[-1])))
    #             )

    #             if start_file <= 0:
    #                 #start_file = start_file[:-1] + [float('nan')]
    #                 start_file = np.nan
    #                 end_file = np.nan
    #                 #end_file = start_file[:-1] + [float('nan')]

    #         else:
    #             start_file = np.nan
    #             end_file = np.nan
    #             lick_tr_total.append(0)
    #             lick_tr_times_relative_to_first_lick_after_go.append([])

    #     return start_file, end_file, lick_tr_times_relative_to_first_lick_after_go, lick_tr_total



    #     # TrialsStartFrame = (img.FrameStartTrial & key).fetch('session_epoch_trial_start_frame', order_by='trial')
    #     # trial_num = (img.FrameStartTrial & key).fetch('trial', order_by='trial')

    #     # if len(TrialsStartFrame) == 0:
    #     #     TrialsStartFrame = (img.FrameStartFile & key).fetch('session_epoch_file_start_frame', order_by='session_epoch_file_num')
    #     #     trial_num = (exp2.BehaviorTrial & key).fetch('trial', order_by='trial')
    #     #     TrialsStartFrame = TrialsStartFrame[trial_num]

    #     # if flag_electric_video == 1:
    #     #     LICK_VIDEO = []  # We align based on electric lickport, even if video does exist
    #     # elif flag_electric_video == 2:
    #     #     LICK_VIDEO = (tracking.VideoNthLickTrial & key).fetch('lick_time_onset_relative_to_trial_start')  # video-based lick detection

    #     # go_time = (exp2.BehaviorTrial.Event & key & 'trial_event_type="go"').fetch('trial_event_time')
    #     # LICK_ELECTRIC = (exp2.ActionEvent & key).fetch()

    #     # lick_tr_times_relative_to_first_lick_after_go = []
    #     # lick_tr_total = []

    #     # for i_tr in range(len(trial_num)):
    #     #     if len(LICK_VIDEO) > 0:
    #     #         all_licks = [LICK_VIDEO[np.where(LICK_VIDEO['trial'] == trial_num[i_tr])]['lick_time_onset_relative_to_trial_start']]
    #     #         licks_after_go = all_licks[all_licks > go_time[i_tr]]
    #     #     else:
    #     #         all_licks = [LICK_ELECTRIC[np.where(LICK_ELECTRIC['trial'] == trial_num[i_tr])]['action_event_time']]
    #     #         licks_after_go = all_licks[all_licks > go_time[i_tr]]

    #     #     if len(licks_after_go) > 0:
    #     #         start_file = TrialsStartFrame[i_tr] + int(licks_after_go[0] * frame_rate) + int(time_bin[0] * frame_rate)
    #     #         end_file = start_file + int((time_bin[1] - time_bin[0]) * frame_rate) - 1

    #     #         lick_tr_times_relative_to_first_lick_after_go.append(all_licks - licks_after_go[0])
    #     #         lick_tr_total.append(
    #     #             np.sum((lick_tr_times_relative_to_first_lick_after_go[i_tr] >= time_bin[0]) &
    #     #                    (lick_tr_times_relative_to_first_lick_after_go[i_tr] <= time_bin[-1]))
    #     #         )

    #     #         if start_file <= 0:
    #     #             start_file = None
    #     #             end_file = None
    #     #     else:
    #     #         start_file = None
    #     #         end_file = None
    #     #         lick_tr_total.append(0)
    #     #         lick_tr_times_relative_to_first_lick_after_go.append([])

    #     # return start_file, end_file, lick_tr_times_relative_to_first_lick_after_go, lick_tr_total



    # # ## tz ##
    # #     import datajoint as dj
    # #     import numpy as np
    # #     from datajoint import fetch
    # #     img= dj.schema('arseny_learning_imaging')
    # #     img= dj.VirtualModule('img', 'arseny_learning_imaging')
    # #     tracking= dj.schema('arseny_learning_tracking')
    # #     tracking= dj.VirtualModule('tracking', 'arseny_learning_tracking')
    # #     exp2= dj.schema('arseny_s1alm_experiment2')
    # #     exp2= dj.VirtualModule ('exp2', 'arseny_s1alm_experiment2')
    # #     key = {'key': ''}  # specify the key
    # #     # Fetch TrialsStartFrame and trial_nums1alm_experiment2')
    # #     # key = {'key': ''}  # specify the key 
    # #     TrialsStartFrame = ((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch ('session_epoch_trial_start_frame', order_by= 'trial') 
    # #     trial_num =((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch ('trial',order_by= 'trial')
    # #     TrialsStartFrame = ((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch('session_epoch_trial_start_frame', order_by='trial')
    # #     trial_num = ((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch('trial', order_by='trial')

    # #     if len(TrialsStartFrame) == 0:  # If it's not mesoscope recording
    # #         TrialsStartFrame = (img.FrameStartFile & key).fetch('session_epoch_file_start_frame', order_by='session_epoch_file_num')
    # #         trial_num = ((exp2.BehaviorTrial & key) - tracking.VideoGroomingTrial).fetch('trial', order_by='trial')
    # #         TrialsStartFrame = TrialsStartFrame[trial_num]

    # #     if flag_electric_video == 1:
    # #         LICK_VIDEO = []  # Align based on electric lickport, even if video does not exist
    # #     elif flag_electric_video == 2:
    # #         # Align based on video, if it exists (align to the first video-detected lick after lickport movement)
    # #         LICK_VIDEO = ((tracking.VideoNthLickTrial & key) - tracking.VideoGroomingTrial).fetch('lick_time_onset_relative_to_trial_start')
    # #         print('WARNING - Commented out "tracking" section here')

    # #     # Align to the first detected lick after Go cue
    # #     go_time = ((exp2.BehaviorTrial.Event & key) - tracking.VideoGroomingTrial & 'trial_event_type="go"').fetch('trial_event_time')
    # #     LICK_ELECTRIC = ((exp2.ActionEvent & key) - tracking.VideoGroomingTrial).fetch()

    # #     lick_tr_times_relative_to_first_lick_after_go = []
    # #     lick_tr_total = []

    # #     for i_tr in range(len(trial_num)):
    # #         if len(LICK_VIDEO) > 0:
    # #             all_licks = [LICK_VIDEO[LICK_VIDEO['trial'] == trial_num[i_tr]]['lick_time_onset_relative_to_trial_start']]
    # #             licks_after_go = all_licks[all_licks > go_time[i_tr]]
    # #         else:
    # #             all_licks = [LICK_ELECTRIC[LICK_ELECTRIC['trial'] == trial_num[i_tr]]['action_event_time']]
    # #             licks_after_go = all_licks[all_licks > go_time[i_tr]]

    # #         if len(licks_after_go) > 0:
    # #             start_file = TrialsStartFrame[i_tr] + int(licks_after_go[0] * frame_rate) + int(time_bin[0] * frame_rate)
    # #             end_file = start_file + int((time_bin[1] - time_bin[0]) * frame_rate) - 1

    # #             lick_tr_times_relative_to_first_lick_after_go.append(all_licks - licks_after_go[0])
    # #             lick_tr_total.append(sum(
    # #                 (lick_tr_times_relative_to_first_lick_after_go[i_tr] >= time_bin[0]) &
    # #                 (lick_tr_times_relative_to_first_lick_after_go[i_tr] <= time_bin[-1])
    # #             ))

    # #             if start_file <= 0:
    # #                 start_file = None
    # #                 end_file = None
    # #         else:
    # #             start_file = None
    # #             end_file = None
    # #             lick_tr_total.append(0)
    # #             lick_tr_times_relative_to_first_lick_after_go.append([])

    # #     return start_file, end_file, lick_tr_times_relative_to_first_lick_after_go, lick_tr_total

    # # ## end tz ##

    # #     import datajoint as dj
    # #     import numpy as np
    # #     from datajoint import fetch
    # #     img= dj.schema('arseny_learning_imaging')
    # #     img= dj.VirtualModule('img', 'arseny_learning_imaging')
    # #     tracking= dj.schema('arseny_learning_tracking')
    # #     tracking= dj.VirtualModule('tracking', 'arseny_learning_tracking')
    # #     exp2= dj.schema('arseny_s1alm_experiment2')
    # #     exp2= dj.VirtualModule ('exp2', 'arseny_s1alm_experiment2')
    # #    # key = {'key': ''}  # specify the key 
    # #     TrialsStartFrame = ((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch ('session_epoch_trial_start_frame', order_by= 'trial') 
    # #     trial_num=((img.FrameStartTrial & key) - tracking.VideoGroomingTrial).fetch ('trial',order_by= 'trial')

    # #     if len(TrialsStartFrame) == "0":
    # #         TrialsStartFrame= ((img.FrameStartFile & key)- tracking.VideoGroomingTrial).fetch ('session_epoch_file_start_frame', order_by='session_epoch_file_num')
    # #         trial_num=((exp2.BehaviorTrial & key) - tracking.VideoGroomingTrial).fetch ('trial',order_by= 'trial')
    # #         TrialsStartFrame= TrialsStartFrame(trial_num)


    # #     if flag_electric_video == 1:
    # #             LICK_VIDEO = []  # Align based on electric lickport, even if video does not exist
    # #     elif flag_electric_video == 2:
    # #             # Align based on video, if it exists (align to the first video-detected lick after lickport movement)
    # #             LICK_VIDEO = (tracking.VideoNthLickTrial() & key - tracking.VideoGroomingTrial).fetch(
    # #                 'lick_time_onset_relative_to_trial_start')
    # #             print('WARNING - Commented out "tracking" section here')

    # #         # Align to the first detected lick after Go cue
    # #     go_time = ((exp2.BehaviorTrial.Event() & key - tracking.VideoGroomingTrial) & 'trial_event_type="go"').fetch(
    # #             'trial_event_time')
    # #     LICK_ELECTRIC = (exp2.ActionEvent() & key - tracking.VideoGroomingTrial).fetch()

    # #     lick_tr_times_relative_to_first_lick_after_go = []
    # #     lick_tr_total = []

    # #     for i_tr in range(len(trial_num)):
    # #         if len(LICK_VIDEO) > 0:
    # #             all_licks = [LICK_VIDEO[LICK_VIDEO['trial'] == trial_num[i_tr]]['lick_time_onset_relative_to_trial_start']]
    # #             licks_after_go = all_licks[all_licks > go_time[i_tr]]
    # #         else:
    # #             all_licks = [LICK_ELECTRIC[LICK_ELECTRIC['trial'] == trial_num[i_tr]]['action_event_time']]
    # #             licks_after_go = all_licks[all_licks > go_time[i_tr]]

    # #         if len(licks_after_go) > 0:
    # #             start_file = TrialsStartFrame[i_tr] + int(licks_after_go[0] * frame_rate) + int(time_bin[0] * frame_rate)
    # #             end_file = start_file + int((time_bin[1] - time_bin[0]) * frame_rate) - 1

    # #             lick_tr_times_relative_to_first_lick_after_go.append(all_licks - licks_after_go[0])
    # #             lick_tr_total.append(sum(
    # #                 (lick_tr_times_relative_to_first_lick_after_go[i_tr] >= time_bin[0]) &
    # #                 (lick_tr_times_relative_to_first_lick_after_go[i_tr] <= time_bin[-1])
    # #                 ))

    # #             if start_file <= 0:
    # #                 start_file = None
    # #                 end_file = None
    # #         else:
    # #             start_file = None
    # #             end_file = None
    # #             lick_tr_total.append(0)
    # #             lick_tr_times_relative_to_first_lick_after_go.append([])

    # #         return start_file, end_file, lick_tr_times_relative_to_first_lick_after_go, lick_tr_total


    # #     # if flag_electric_video == 1:
    # #     #         lickvideo = [] #We align based on electric lickport, even if video does exist
    # #     # elif flag_electric_video == 2: #We  try to align based on video, if it exists.
    # #     #         # We align to the first video-detected lick after lickport movement
    # #     #         lickvideo = ((tracking.VideoNthLickTrial & key) - tracking.VideoGroomingTrial).fetch('lick_time_onset_relative_to_trial_start')# we use it to get the timing of licks after lickport entrance

    # #     # ## multiple options for alignment- test all and compare between them (appearance of lickport (first contact lick, go cue in this case), first lick-w or w/o lickport appearance)

    # #     # # align to the first detected lick after go cue
    # #     # #######
    # #     # # BehaviorTrialEvent table in schema exp2 is defiend as dj.part, and to access it one must access the parent table BehaviorTrial. syntax: schema.parent_table.table
    # #     # go_time = ((exp2.BehaviorTrial.Event & key) - tracking.VideoGroomingTrial & 'trial_event_type="go"').fetch('trial_event_time')
    # #     # lick_electric=((exp2.ActionEvent & key) - tracking.VideoGroomingTrial).fetch() # fetch all

    # #     # lick_tr_times_relative_to_first_lick_after_go = []
    # #     # lick_tr_total = []

    # #     # for i_tr in range(len(trial_num)):
    # #     #     if len(lickvideo) != 0:
    # #     #         all_licks = [lick['lick_time_onset_relative_to_trial_start'] for lick in lickvideo if lick['trial'] == trial_num[i_tr]]
    # #     #         licks_after_go = [lick for lick in all_licks if lick > go_time[i_tr]]
    # #     #     else:
    # #     #         all_licks = [lick['action_event_time'] for lick in lick_electric if lick['trial'] == trial_num[i_tr]]
    # #     #         licks_after_go = [lick for lick in all_licks if lick > go_time[i_tr]]
            
    # #     #     if len(licks_after_go) != 0:
    # #     #         start_file = TrialsStartFrame[i_tr] + int(float(licks_after_go[0]) * frame_rate) + int(float(time_bin[0]) * frame_rate)
    # #     #         end_file = start_file + int((float(time_bin[1]) - float(time_bin[0])) * frame_rate) - 1
                
    # #     #         lick_tr_times_relative_to_first_lick_after_go.append(np.array(all_licks) - licks_after_go[0])
    # #     #         lick_tr_total.append(np.sum((np.array(lick_tr_times_relative_to_first_lick_after_go[i_tr]) >= time_bin[0]) & 
    # #     #                                     (np.array(lick_tr_times_relative_to_first_lick_after_go[i_tr]) <= time_bin[-1])))
                
    # #     #         if start_file <= 0:
    # #     #             start_file = np.nan
    # #     #             end_file = np.nan
    # #     #     else:
    # #     #         start_file = np.nan
    # #     #         end_file = np.nan
    # #     #         lick_tr_total.append(0)
    # #     #         lick_tr_times_relative_to_first_lick_after_go.append([])


    # #     # # start_file = np.zeros(len(trialnum))
    # #     # # end_file = np.zeros(len(trialnum))
    # #     # # lick_tr_times_relative_to_first_lick_after_go = []
    # #     # # lick_tr_total = np.zeros(len(trialnum))

    # #     # # for i_tr, trial in enumerate(trialnum):
    # #     # #     if len(lickvideo) > 0:
    # #     # #         all_licks = lickvideo[[lick['trial'] == trial for lick in lickvideo]]
    # #     # #         all_licks = [lick[0] for lick in all_licks]
    # #     # #         licks_after_go = [lick for lick in all_licks if lick > gotime[i_tr]]
    # #     # #     else: #use electric
    # #     # #         all_licks = lickelectric[[lick['trial'] == trial for lick in lickelectric]]
    # #     # #         all_licks = [lick[2] for lick in all_licks]
    # #     # #         licks_after_go = [lick for lick in all_licks if lick > gotime[i_tr]]


        
