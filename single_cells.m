% %% fetch
data = fetch(LICK2Dtal.ROILick2DPSTHSpikes,'*');
block = fetch(LICK2Dtal.ROILick2DPSTHBlockSpikes, '*');
%fetch stats
datastat=fetch(LICK2Dtal.ROILick2DPSTHStatsSpikes,'*');
blockstat=fetch(LICK2Dtal.ROILick2DPSTHBlockStatsSpikes,'*');
%% regular+small+large
% by subject
% Get unique subject_id values
save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\reward';

unique_subject_ids = unique([data.subject_id]);

% Iterate over unique subject_id values
for i = 1:numel(unique_subject_ids)
    target_subject_id = unique_subject_ids(1);

    % Find rows with the same subject_id
    rows = data([data.subject_id] == target_subject_id);

    % Choose up to 1000 rows
    num_rows = min(1000, numel(rows));

    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        
        psth_regular = row_data.psth_regular;
        psth_small = row_data.psth_small;
        psth_large = row_data.psth_large;
        psth_time = row_data.psth_time;
        psth_regular_stem = row_data.psth_regular_stem;
        psth_small_stem = row_data.psth_small_stem;
        psth_large_stem = row_data.psth_large_stem;

        % Create a new figure for each row
        figure('Visible', 'off');
        hold on;

        % Plot the shaded region for psth_regular
        curve1=psth_regular+psth_regular_stem;
        curve2=psth_regular-psth_regular_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'b', 'FaceAlpha', 0.3);
        %shaded_region = [psth_regular - psth_regular_stem; psth_regular + psth_regular_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region(:)', 'b', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular
        plot(psth_time, psth_regular, 'b', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_small
        curve1=psth_small+psth_small_stem;
        curve2=psth_small-psth_small_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'r', 'FaceAlpha', 0.3);
        %shaded_region_small = [psth_small - psth_small_stem; psth_small + psth_small_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_small(:)', 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_small
        plot(psth_time, psth_small, 'r', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_large
        curve1=psth_large+psth_large_stem;
        curve2=psth_large-psth_large_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'g', 'FaceAlpha', 0.3);
        %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_large, 'g', 'LineWidth', 1.5);
        

        legend('R-stem', 'regular', 'S-stem', 'small', 'L-stem', 'large');
        hold on;
        % Add labels to the plot
        title(sprintf('Subject ID: %d - roi_number: %d - Session: %d', target_subject_id, row_data.roi_number, row_data.session));
        xlabel('T');
        ylabel('PSTH');

        % Save the figure as JPG
        save_name = sprintf('Subject_%d_roi_number_%d_Session_%d.jpg', target_subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end

%% regular+small+large norm

%data = fetch(LICK2Dtal.ROILick2DPSTHSpikes, '*');
%block = fetch(LICK2Dtal.ROILick2DPSTHBlockSpikes, '*');
% by subject
% Get unique subject_id values
save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\norm_reward';
unique_subject_ids = unique([data.subject_id]);

% Iterate over unique subject_id values
for i = 1:numel(unique_subject_ids)
    target_subject_id = unique_subject_ids(1);

    % Find rows with the same subject_id
    rows = data([data.subject_id] == target_subject_id);

    % Choose up to 1000 rows
    num_rows = min(1000, numel(rows));

    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        
        psth_regular = row_data.psth_regular;
        psth_small = row_data.psth_small;
        psth_large = row_data.psth_large;
        psth_time = row_data.psth_time;
        psth_regular_stem = row_data.psth_regular_stem;
        psth_small_stem = row_data.psth_small_stem;
        psth_large_stem = row_data.psth_large_stem;
        
        peak_regular = max(psth_regular);
        peak_small = max(psth_small);
        peak_large = max(psth_large);
        
        psth_regular = psth_regular / peak_regular;
        psth_small = psth_small / peak_small;
        psth_large = psth_large / peak_large;
           
        psth_regular_stem = psth_regular_stem / peak_regular;
        psth_small_stem = psth_small_stem / peak_small;
        psth_large_stem = psth_large_stem / peak_large;


        % Create a new figure for each row
        figure('Visible', 'off');
        hold on;

        % Plot the shaded region for psth_regular
        curve1=psth_regular+psth_regular_stem;
        curve2=psth_regular-psth_regular_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'b', 'FaceAlpha', 0.3);
        %shaded_region = [psth_regular - psth_regular_stem; psth_regular + psth_regular_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region(:)', 'b', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular
        plot(psth_time, psth_regular, 'b', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_small
        curve1=psth_small+psth_small_stem;
        curve2=psth_small-psth_small_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'r', 'FaceAlpha', 0.3);
        %shaded_region_small = [psth_small - psth_small_stem; psth_small + psth_small_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_small(:)', 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_small
        plot(psth_time, psth_small, 'r', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_large
        curve1=psth_large+psth_large_stem;
        curve2=psth_large-psth_large_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'g', 'FaceAlpha', 0.3);
        %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_large, 'g', 'LineWidth', 1.5);
        

        legend('R-stem', 'regular', 'S-stem', 'small', 'L-stem', 'large');
        hold on;
        % Add labels to the plot
        title(sprintf('Norm R- Subject ID: %d - roi_number: %d - Session: %d', target_subject_id, row_data.roi_number, row_data.session));
        xlabel('T');
        ylabel('PSTH');

        % Save the figure as JPG
        save_name = sprintf('Norm_Subject_%d_roi_number_%d_Session_%d.jpg', target_subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end

%% Block

unique_subject_ids = unique([data.subject_id]);
save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\block';

% Iterate over unique subject_id values
for i = 1:numel(unique_subject_ids)
    target_subject_id = unique_subject_ids(i);

    % Find rows with the same subject_id
    rows = block([block.subject_id] == target_subject_id);
    rows1= data([data.subject_id] == target_subject_id);

    % Choose up to 1000 rows
    num_rows = min(1000, numel(rows));
    
    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        time_row= rows1(j);

        
        psth_first = row_data.psth_first;
        psth_begin = row_data.psth_begin;
        psth_mid = row_data.psth_mid;
        psth_end = row_data.psth_end;
        psth_time = time_row.psth_time;
        psth_first_stem = row_data.psth_first_stem;
        psth_begin_stem = row_data.psth_begin_stem;
        psth_mid_stem = row_data.psth_mid_stem;
        psth_end_stem = row_data.psth_end_stem;
        % Create a new figure for each row
        figure('Visible', 'off');
        hold on;

        % Plot the shaded region for psth_regular
        curve1=psth_first+psth_first_stem;
        curve2=psth_first-psth_first_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'b', 'FaceAlpha', 0.3);
        %shaded_region = [psth_regular - psth_regular_stem; psth_regular + psth_regular_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region(:)', 'b', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular
        plot(psth_time, psth_first, 'b', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_small
        curve1=psth_begin+psth_begin_stem;
        curve2=psth_begin-psth_begin_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'r', 'FaceAlpha', 0.3);
        %shaded_region_small = [psth_small - psth_small_stem; psth_small + psth_small_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_small(:)', 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_small
        plot(psth_time, psth_begin, 'r', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_large
        curve1=psth_mid+psth_mid_stem;
        curve2=psth_mid-psth_mid_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'g', 'FaceAlpha', 0.3);
        %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_mid, 'g', 'LineWidth', 1.5);
        

        % Plot the shaded region for psth_regular_large
        curve1=psth_end+psth_end_stem;
        curve2=psth_end-psth_end_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'black', 'FaceAlpha', 0.3);
        %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_end, 'black', 'LineWidth', 1.5);
        
        legend('F-stem', 'PSTH First', 'B-stem', 'PSTH Begin', 'M-stem', 'PSTH Mid', 'E-stem', 'PSTH_End');
        hold on;
        % Add labels to the plot
        title(sprintf('Subject ID: %d - roi_number: %d - Session: %d', target_subject_id, row_data.roi_number, row_data.session));
        xlabel('Time to Lick');
        ylabel('PSTH');

        % Save the figure as JPG
        save_name = sprintf('Block - Subject_%d_roi_number_%d_Session_%d.jpg', target_subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end

%% norm block

%data = fetch(LICK2Dtal.ROILick2DPSTHSpikes, '*');
%block = fetch(LICK2Dtal.ROILick2DPSTHBlockSpikes, '*');
% by subject
% Get unique subject_id values
unique_subject_ids = unique([block.subject_id]);
save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\norm_block';

% Iterate over unique subject_id values
for i = 1:numel(unique_subject_ids)
    target_subject_id = unique_subject_ids(1);

    % Find rows with the same subject_id
    rows = block([block.subject_id] == target_subject_id);
    rows1= data([data.subject_id] == target_subject_id);
    % Choose up to 1000 rows
    num_rows = min(1000, numel(rows));
    
    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        time_row= rows1(j);
        %time_row = data([data.subject_id] == row_data.subject_id & [data.session] == row_data.session & [data.roi_number] == row_data.roi_number);
        %psth_time = time_row.psth_time;
        
        psth_first = row_data.psth_first;
        psth_begin = row_data.psth_begin;
        psth_mid = row_data.psth_mid;
        psth_end = row_data.psth_end;
        psth_time = time_row.psth_time;
        psth_first_stem = row_data.psth_first_stem;
        psth_begin_stem = row_data.psth_begin_stem;
        psth_mid_stem = row_data.psth_mid_stem;
        psth_end_stem = row_data.psth_end_stem;
        
        peak_first = max(psth_first);
        peak_begin = max(psth_begin);
        peak_mid = max(psth_mid);
        peak_end = max(psth_end);
        
        psth_first = psth_first / peak_first;
        psth_begin = psth_begin / peak_begin;
        psth_mid = psth_mid / peak_mid;
        psth_end = psth_end / peak_end;
        
        psth_first_stem = psth_first_stem / peak_first;
        psth_begin_stem = psth_begin_stem / peak_begin;
        psth_mid_stem = psth_mid_stem / peak_mid;
        psth_end_stem = psth_end_stem / peak_end;

        % Create a new figure for each row
        figure('Visible', 'off');
        hold on;
        
        % Plot the shaded region for psth_regular
        curve1=psth_first+psth_first_stem;
        curve2=psth_first-psth_first_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'b', 'FaceAlpha', 0.3);
        %shaded_region = [psth_regular - psth_regular_stem; psth_regular + psth_regular_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region(:)', 'b', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular
        plot(psth_time, psth_first, 'b', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_small
        curve1=psth_begin+psth_begin_stem;
        curve2=psth_begin-psth_begin_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'r', 'FaceAlpha', 0.3);
        %shaded_region_small = [psth_small - psth_small_stem; psth_small + psth_small_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_small(:)', 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_small
        plot(psth_time, psth_begin, 'r', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_large
        curve1=psth_mid+psth_mid_stem;
        curve2=psth_mid-psth_mid_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'g', 'FaceAlpha', 0.3);
        %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_mid, 'g', 'LineWidth', 1.5);
        

        % Plot the shaded region for psth_regular_large
        curve1=psth_end+psth_end_stem;
        curve2=psth_end-psth_end_stem;
        x2=[psth_time, fliplr(psth_time)];
        inbetween=[curve1, fliplr(curve2)];
        fill(x2,inbetween, 'black', 'FaceAlpha', 0.3);
        %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_end, 'black', 'LineWidth', 1.5);
    
        legend('F-stem', 'PSTH First', 'B-stem', 'PSTH Begin', 'M-stem', 'PSTH Mid', 'E-stem', 'PSTH_End');
        hold on;
        % Add labels to the plot
        title(sprintf('Block-Norm - Subject ID: %d - roi_number: %d - Session: %d', target_subject_id, row_data.roi_number, row_data.session));
        xlabel('T');
        ylabel('PSTH');

        % Save the figure as JPG
        save_name = sprintf('Block_Norm_Subject_%d_roi_number_%d_Session_%d.jpg', target_subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end
%% regular odd, even
save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\regular';

unique_subject_ids = unique([data.subject_id]);
unique_session = unique([data.session]); 

% Iterate over unique subject_id values
for i = 1:numel(unique_session)
    target_session = unique_session(i+2);

    % Find rows with the same subject_id
    rows = data([data.session] == target_session);

    % Choose up to 1000 rows
    num_rows = min(10, numel(rows));

    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        
        psth_regular = row_data.psth_regular;
        psth_regular_odd = row_data.psth_regular_odd;
        psth_regular_even = row_data.psth_regular_even;
        psth_time = row_data.psth_time;

%         psth_regular_stem = row_data.psth_regular_stem;
%         psth_small_stem = row_data.psth_small_stem;
%         psth_large_stem = row_data.psth_large_stem;

        % Create a new figure for each row
        figure('Visible', 'off');
        hold on;

        % Plot the shaded region for psth_regular
%         curve1=psth_regular+psth_regular_stem;
%         curve2=psth_regular-psth_regular_stem;
%         x2=[psth_time, fliplr(psth_time)];
%         inbetween=[curve1, fliplr(curve2)];
%         fill(x2,inbetween, 'b', 'FaceAlpha', 0.3);
        %shaded_region = [psth_regular - psth_regular_stem; psth_regular + psth_regular_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region(:)', 'b', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular
        plot(psth_time, psth_regular, 'b', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_small
%         curve1=psth_small+psth_small_stem;
%         curve2=psth_small-psth_small_stem;
%         x2=[psth_time, fliplr(psth_time)];
%         inbetween=[curve1, fliplr(curve2)];
%         fill(x2,inbetween, 'r', 'FaceAlpha', 0.3);
%         %shaded_region_small = [psth_small - psth_small_stem; psth_small + psth_small_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_small(:)', 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_small
        plot(psth_time, psth_regular_odd, 'r', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_large
%         curve1=psth_large+psth_large_stem;
%         curve2=psth_large-psth_large_stem;
%         x2=[psth_time, fliplr(psth_time)];
%         inbetween=[curve1, fliplr(curve2)];
%         fill(x2,inbetween, 'g', 'FaceAlpha', 0.3);
%         %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_regular_even, 'g', 'LineWidth', 1.5);
        

        legend('regular', 'odd', 'even');
        hold on;
        % Add labels to the plot
        title(sprintf('Subject ID: %d - roi_number: %d - Session: %d', target_subject_id, row_data.roi_number, row_data.session));
        xlabel('T');
        ylabel('PSTH');

        % Save the figure as JPG
        save_name = sprintf('Subject_%d_roi_number_%d_Session_%d.jpg', target_subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end

%% 
save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\small_large_regular';

unique_subject_ids = unique([data.subject_id]);

% Iterate over unique subject_id values
for i = 1:numel(unique_subject_ids)
    target_subject_id = unique_subject_ids(1);

    % Find rows with the same subject_id
    rows = data([data.subject_id] == target_subject_id);

    % Choose up to 1000 rows
    num_rows = min(100, numel(rows));

    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        
        psth_small = row_data.psth_small;
        psth_small_odd = row_data.psth_small_odd;
        psth_small_even = row_data.psth_small_even;
%         psth_large = row_data.psth_small;
%         psth_large_odd = row_data.psth_small_odd;
%         psth_large_even = row_data.psth_small_even;
%         psth_regular = row_data.psth_small;
%         psth_regular_odd = row_data.psth_small_odd;
%         psth_regular_even = row_data.psth_small_even;
        psth_time = row_data.psth_time;

%         psth_regular_stem = row_data.psth_regular_stem;
%         psth_small_stem = row_data.psth_small_stem;
%         psth_large_stem = row_data.psth_large_stem;

        % Create a new figure for each row
        figure('Visible', 'off');
        hold on;

        % Plot the shaded region for psth_regular
%         curve1=psth_regular+psth_regular_stem;
%         curve2=psth_regular-psth_regular_stem;
%         x2=[psth_time, fliplr(psth_time)];
%         inbetween=[curve1, fliplr(curve2)];
%         fill(x2,inbetween, 'b', 'FaceAlpha', 0.3);
        %shaded_region = [psth_regular - psth_regular_stem; psth_regular + psth_regular_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region(:)', 'b', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular
        plot(psth_time, psth_small, 'b', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_small
%         curve1=psth_small+psth_small_stem;
%         curve2=psth_small-psth_small_stem;
%         x2=[psth_time, fliplr(psth_time)];
%         inbetween=[curve1, fliplr(curve2)];
%         fill(x2,inbetween, 'r', 'FaceAlpha', 0.3);
%         %shaded_region_small = [psth_small - psth_small_stem; psth_small + psth_small_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_small(:)', 'r', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_small
        plot(psth_time, psth_small_odd, 'r', 'LineWidth', 1.5);

        % Plot the shaded region for psth_regular_large
%         curve1=psth_large+psth_large_stem;
%         curve2=psth_large-psth_large_stem;
%         x2=[psth_time, fliplr(psth_time)];
%         inbetween=[curve1, fliplr(curve2)];
%         fill(x2,inbetween, 'g', 'FaceAlpha', 0.3);
%         %shaded_region_large = [psth_large - psth_large_stem; psth_large + psth_large_stem];
        %fill([psth_time, fliplr(psth_time)], shaded_region_large(:)', 'g', 'FaceAlpha', 0.3, 'EdgeColor', 'none');

        % Plot the line for psth_regular_large
        plot(psth_time, psth_small_even, 'g', 'LineWidth', 1.5);
        

        legend('small', 'odd', 'even');
        hold on;
        % Add labels to the plot
        title(sprintf('Subject ID: %d - roi_number: %d - Session: %d', target_subject_id, row_data.roi_number, row_data.session));
        xlabel('T');
        ylabel('PSTH');

        % Save the figure as JPG
        save_name = sprintf('Subject_%d_roi_number_%d_Session_%d.jpg', target_subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end
%%
% %% fetch
data = fetch(LICK2Dtal.ROILick2DPSTHSpikes,'*');%for psth
data1 = fetch(IMG.ROISpikes & (IMG.ROI-IMG.ROIBad),'*');%for dff
block = fetch(LICK2Dtal.ROILick2DPSTHBlockSpikes, '*');
%fetch stats
datastat=fetch(LICK2Dtal.ROILick2DPSTHStatsSpikes,'*');
blockstat=fetch(LICK2Dtal.ROILick2DPSTHBlockStatsSpikes,'*');
% fetch roi_number_uid
uid = fetch((IMG.ROI-IMG.ROIBad),'roi_number_uid');%,'ORDER BY roi_number');

%% plot 3 subplots in one figure- regular+odd+even, reward, block (session >1)

%save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\020723';
save_dir = 'D:\user\Desktop\New folder\plots'
unique_subject_ids = unique([data.subject_id]);
unique_session = unique([data.session]); 

% Iterate over unique subject_id values
for i = 1:numel(unique_session)
    target_session = unique_session(i+1);

    % Find rows with the same subject_id
    rows = data([data.session] == target_session);
    rows1 = block([block.session] == target_session);
    rows2 = datastat([datastat.session]==target_session);
    rows3= blockstat([blockstat.session]==target_session);
    rows4= uid([uid.session]==target_session);
    % Choose up to 1000 rows
    num_rows = min(200, numel(rows));

    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        row_block = rows1(j);%(find(rows1(i)== rows(j)));
        row_d_stats = rows2(j);
        row_b_stats = rows3(j);
%         for n=1:num_rows
%             if [rows4.subject_id(n)==row_d_stats.subject_id] && [rows4.roi_number(n)==row_d_stats.roi_number]
%                 row_uid= rows4(n);
%             end
%         end
        row_uid = uid([uid.subject_id] == rows(j).subject_id & [uid.roi_number] == rows(j).roi_number & [uid.session] == target_session);
        %row_uid= rows4(n);
    
        %regular
        psth_regular = row_data.psth_regular;
        psth_regular_odd = row_data.psth_regular_odd;
        psth_regular_even = row_data.psth_regular_even;
        psth_time = row_data.psth_time;
        %block
        psth_first = row_block.psth_first;
        psth_begin = row_block.psth_begin;
        psth_mid = row_block.psth_mid;
        psth_end = row_block.psth_end;
        psth_time = row_data.psth_time;
        % reward
        psth_regular = row_data.psth_regular;
        psth_small = row_data.psth_small;
        psth_large = row_data.psth_large;
        psth_time = row_data.psth_time;
        

%         psth_regular_stem = row_data.psth_regular_stem;
%         psth_small_stem = row_data.psth_small_stem;
%         psth_large_stem = row_data.psth_large_stem;
        minv=min(min([(psth_regular), min(psth_small), min(psth_large), min(psth_first), min(psth_begin), min(psth_mid), min(psth_end)]));
        maxv=max(max([(psth_regular), max(psth_small), max(psth_large), max(psth_first), max(psth_begin), max(psth_mid), max(psth_end)]));
        
        titlestats_regular_small=sprintf('\\fontsize{6}regular vs. small  r=  %.04f, p-value=  %.04f', row_d_stats.psth_regular_vs_small_corr, row_d_stats.reward_mean_pval_regular_small);
        titlestats_regular_large=sprintf('\\fontsize{6}regular vs. large  r= %.04f, p-value= %.04f', row_d_stats.psth_regular_vs_large_corr, row_d_stats.reward_mean_pval_regular_large);
        titlestats_large_small=sprintf('\\fontsize{6}small vs. large  r= %.04f, p-value= %.04f', row_d_stats.psth_small_vs_large_corr, row_d_stats.reward_mean_pval_small_large);
        titlereg= sprintf('\\fontsize{6}r= %.04f%', row_d_stats.psth_regular_odd_vs_even_corr);
        ann_psth_first_vs_begin=sprintf('first vs. begin  r=  %.04f, p-value=  %.04f', row_b_stats.psth_first_vs_begin_corr, row_b_stats.block_peak_pval_first_begin);
        ann_psth_first_vs_mid=sprintf('first vs. mid  r=  %.04f', row_b_stats.psth_first_vs_mid_corr);
        ann_psth_first_vs_end=sprintf('first vs. end  r=  %.04f, p-value=  %.04f', row_b_stats.psth_first_vs_end_corr, row_b_stats.block_peak_pval_first_end);
        ann_psth_begin_vs_end=sprintf('begin vs. end  r=  %.04f', row_b_stats.psth_begin_vs_mid_corr);
        ann_psth_begin_vs_mid=sprintf('begin vs. mid  r=  %.04f, p-value=  %.04f', row_b_stats.psth_begin_vs_end_corr, row_b_stats.block_peak_pval_begin_end);
        ann_psth_mid_vs_end=sprintf('mid vs. end  r=  %.04f', row_b_stats.psth_mid_vs_end_corr);

        % Create a new figure for each row
        figure('Visible', 'off');
        set(gcf,'DefaultAxesFontName','helvetica');
        set(gcf,'PaperUnits','centimeters','PaperPosition',[0 0 25 30]);
        set(gcf,'PaperOrientation','portrait');
        set(gcf,'Units','centimeters','Position',get(gcf,'paperPosition')+[3 0 0 0]);
        set(gcf,'color',[1 1 1]);

        hold on;
        subplot(3,1,1)
        plot(psth_time, psth_regular, 'b', 'LineWidth', 1.5);
        hold on;
        hold on;
        plot(psth_time, psth_regular_odd, 'color',[0.3010 0.7450 0.9330], 'LineWidth', 1.5); 
        hold on;
        plot(psth_time, psth_regular_even, 'color',[0.3010 0.7450 0.9330], 'LineWidth', 1.5);
        hold on;
        title({'Regular'; titlereg});
        legend({'regular', 'odd', 'even'},'Location', 'eastoutside');
        hold on;
        ylim([minv maxv])
        axis square
        % Add labels to the plot
        xlabel('Time to Lick');
        ylabel('amp');
        
        hold on;
        subplot(3,1,2)
        plot(psth_time, psth_first, 'c', 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_begin, 'm', 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_mid, 'color',[0 0.4470 0.7410], 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_end, 'k', 'LineWidth', 1.5);
        hold on;
        legend({'First', 'Begin', 'Mid', 'End'}, 'Location', 'eastoutside');
        hold on;
        ylim([minv maxv])
        axis square
        xlabel('Time to Lick');
        ylabel('amp');
        hold on;
        %text([ann_psth_first_vs_begin;ann_psth_first_vs_mid;ann_psth_first_vs_end;ann_psth_begin_vs_end;ann_psth_begin_vs_mid;ann_psth_mid_vs_end], 'outside', 'clipping', 'off');
        %text('textbox','String',[{ann_psth_first_vs_begin;ann_psth_first_vs_mid;ann_psth_first_vs_end;ann_psth_begin_vs_end;ann_psth_begin_vs_mid;ann_psth_mid_vs_end}],'HorizontalAlignment','left','VerticalAlignment','bottom','EdgeColor', "none",'FitBoxToText','on', 'FontSize', 10)
        annotation('textbox',[0.003 0 0.6 0.6],'String',[{ann_psth_first_vs_begin;ann_psth_first_vs_mid;ann_psth_first_vs_end;ann_psth_begin_vs_end;ann_psth_begin_vs_mid;ann_psth_mid_vs_end}],'EdgeColor', "none",'FitBoxToText','on', 'FontSize', 10)
        title('Block')
        
        hold on;
        subplot(3,1,3)
        plot(psth_time, psth_small,'color', 'c', 'LineWidth', 1.5); %[0 0.7 0.7]
        hold on;
        plot(psth_time, psth_regular,'color', [0 0.4470 0.7410], 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_large, 'm', 'LineWidth', 1.5);
        hold on;
        legend({'small', 'regular', 'large'}, 'Location', 'eastoutside');
        hold on;
        axis square
        ylim([minv maxv])
        xlabel('Time to Lick');
        ylabel('amp');
        hold on;
        title({'Reward'; titlestats_regular_small; titlestats_regular_large; titlestats_large_small})
        %hold on;
        %annotation('textbox',[0.003 0 0.6 0.6],'String',{titlestats_regular_small; titlestats_regular_large; titlestats_large_small},'EdgeColor', "none",'FitBoxToText','on', 'FontSize', 10);
        %subtitle(subtitleStruct, 'FontSize', 7);
        hold on;
        
       
        hold on;
        txt=sprintf('Subject ID: %d - roi number uid: %d - roi number: %d - Session: %d', row_data.subject_id, row_uid.roi_number_uid, row_data.roi_number, row_data.session);
        sgtitle(txt);
        % Save the figure as JPG
        save_name = sprintf('Subject_%d_roi_number_%d_Session_%d.jpg', row_data.subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end


%% plot dff for specific cell 
% plot 3 subplots in one figure- regular+odd+even, reward, block (session >1)

save_dir = 'C:\Users\talch\AppData\Roaming\MathWorks\single_cells\020723';

unique_subject_ids = 463189;
unique_session = 4; 
unique_roi = 5;
% Iterate over unique subject_id values
for i = 1:numel(unique_session)
    target_session = unique_session(i);

    % Find rows with the same subject_id
    rows = data([data.session] == target_session & [data.roi_number]==unique_roi &[data.session]==4);
    rows1 = block([block.session] == target_session & [block.roi_number]==unique_roi &[block.session]==4);
    rows2 = datastat([datastat.session] == target_session & [datastat.roi_number]==unique_roi &[datastat.session]==4);
    rows3= blockstat([blockstat.session] == target_session & [blockstat.roi_number]==unique_roi &[blockstat.session]==4);
    rows4= uid([uid.session]==target_session);
    % Choose up to 1000 rows
    num_rows = numel(rows);

    % Iterate over the selected rows
    for j = 1:num_rows
        row_data = rows(j);
        row_block = rows1(j);%(find(rows1(i)== rows(j)));
        row_d_stats = rows2(j);
        row_b_stats = rows3(j);
%         for n=1:num_rows
%             if [rows4.subject_id(n)==row_d_stats.subject_id] && [rows4.roi_number(n)==row_d_stats.roi_number]
%                 row_uid= rows4(n);
%             end
%         end
        row_uid = uid([uid.subject_id] == rows(j).subject_id & [uid.roi_number] == rows(j).roi_number & [uid.session] == target_session);
        row_data1=data1([data1.subject_id] == rows(j).subject_id &[data1.roi_number] == rows(j).roi_number & [data1.session] == target_session);
        %row_uid= rows4(n);
    
        dff=row_data1.dff_trace;
        %regular
        psth_regular = row_data.psth_regular;
        psth_regular_odd = row_data.psth_regular_odd;
        psth_regular_even = row_data.psth_regular_even;
        psth_time = row_data.psth_time;
        %block
        psth_first = row_block.psth_first;
        psth_begin = row_block.psth_begin;
        psth_mid = row_block.psth_mid;
        psth_end = row_block.psth_end;
        psth_time = row_data.psth_time;
        % reward
        psth_regular = row_data.psth_regular;
        psth_small = row_data.psth_small;
        psth_large = row_data.psth_large;
        psth_time = row_data.psth_time;
        

%         psth_regular_stem = row_data.psth_regular_stem;
%         psth_small_stem = row_data.psth_small_stem;
%         psth_large_stem = row_data.psth_large_stem;
        minv=min(min([(psth_regular), min(psth_small), min(psth_large), min(psth_first), min(psth_begin), min(psth_mid), min(psth_end)]));
        maxv=max(max([(psth_regular), max(psth_small), max(psth_large), max(psth_first), max(psth_begin), max(psth_mid), max(psth_end)]));
        
        titlestats_regular_small=sprintf('\\fontsize{6}regular vs. small  r=  %.04f, p-value=  %.04f', row_d_stats.psth_regular_vs_small_corr, row_d_stats.reward_mean_pval_regular_small);
        titlestats_regular_large=sprintf('\\fontsize{6}regular vs. large  r= %.04f, p-value= %.04f', row_d_stats.psth_regular_vs_large_corr, row_d_stats.reward_mean_pval_regular_large);
        titlestats_large_small=sprintf('\\fontsize{6}small vs. large  r= %.04f, p-value= %.04f', row_d_stats.psth_small_vs_large_corr, row_d_stats.reward_mean_pval_small_large);
        titlereg= sprintf('\\fontsize{6}r= %.04f%', row_d_stats.psth_regular_odd_vs_even_corr);
        ann_psth_first_vs_begin=sprintf('first vs. begin  r=  %.04f, p-value=  %.04f', row_b_stats.psth_first_vs_begin_corr, row_b_stats.block_peak_pval_first_begin);
        ann_psth_first_vs_mid=sprintf('first vs. mid  r=  %.04f', row_b_stats.psth_first_vs_mid_corr);
        ann_psth_first_vs_end=sprintf('first vs. end  r=  %.04f, p-value=  %.04f', row_b_stats.psth_first_vs_end_corr, row_b_stats.block_peak_pval_first_end);
        ann_psth_begin_vs_end=sprintf('begin vs. end  r=  %.04f', row_b_stats.psth_begin_vs_mid_corr);
        ann_psth_begin_vs_mid=sprintf('begin vs. mid  r=  %.04f, p-value=  %.04f', row_b_stats.psth_begin_vs_end_corr, row_b_stats.block_peak_pval_begin_end);
        ann_psth_mid_vs_end=sprintf('mid vs. end  r=  %.04f', row_b_stats.psth_mid_vs_end_corr);

        % Create a new figure for each row
        figure('Visible', 'off');
        set(gcf,'DefaultAxesFontName','helvetica');
        set(gcf,'PaperUnits','centimeters','PaperPosition',[0 0 25 30]);
        set(gcf,'PaperOrientation','portrait');
        set(gcf,'Units','centimeters','Position',get(gcf,'paperPosition')+[3 0 0 0]);
        set(gcf,'color',[1 1 1]);

        hold on;
        subplot(4,1,4)
        plot(psth_time, dff, 'b', LineWidth, 1.5);
        hold on;
        title({dff})
        xlable('Time to Lick')
        ylable('DF/F')
        axis square
        
        hold on;
        subplot(4,1,1)
        plot(psth_time, psth_regular, 'b', 'LineWidth', 1.5);
        hold on;
        hold on;
        plot(psth_time, psth_regular_odd, 'color',[0.3010 0.7450 0.9330], 'LineWidth', 1.5); 
        hold on;
        plot(psth_time, psth_regular_even, 'color',[0.3010 0.7450 0.9330], 'LineWidth', 1.5);
        hold on;
        title({'Regular'; titlereg});
        legend({'regular', 'odd', 'even'},'Location', 'eastoutside');
        hold on;
        %ylim([minv maxv])
        axis square
        % Add labels to the plot
        xlabel('Time to Lick');
        ylabel('amp');
        
        hold on;
        subplot(4,1,2)
        plot(psth_time, psth_first, 'c', 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_begin, 'm', 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_mid, 'color',[0 0.4470 0.7410], 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_end, 'k', 'LineWidth', 1.5);
        hold on;
        legend({'First', 'Begin', 'Mid', 'End'}, 'Location', 'eastoutside');
        hold on;
        %ylim([minv maxv])
        axis square
        xlabel('Time to Lick');
        ylabel('amp');
        hold on;
        %text([ann_psth_first_vs_begin;ann_psth_first_vs_mid;ann_psth_first_vs_end;ann_psth_begin_vs_end;ann_psth_begin_vs_mid;ann_psth_mid_vs_end], 'outside', 'clipping', 'off');
        %text('textbox','String',[{ann_psth_first_vs_begin;ann_psth_first_vs_mid;ann_psth_first_vs_end;ann_psth_begin_vs_end;ann_psth_begin_vs_mid;ann_psth_mid_vs_end}],'HorizontalAlignment','left','VerticalAlignment','bottom','EdgeColor', "none",'FitBoxToText','on', 'FontSize', 10)
        annotation('textbox',[0.003 0 0.6 0.6],'String',[{ann_psth_first_vs_begin;ann_psth_first_vs_mid;ann_psth_first_vs_end;ann_psth_begin_vs_end;ann_psth_begin_vs_mid;ann_psth_mid_vs_end}],'EdgeColor', "none",'FitBoxToText','on', 'FontSize', 10)
        title('Block')
        
        hold on;
        subplot(4,1,3)
        plot(psth_time, psth_small,'color', 'c', 'LineWidth', 1.5); %[0 0.7 0.7]
        hold on;
        plot(psth_time, psth_regular,'color', [0 0.4470 0.7410], 'LineWidth', 1.5);
        hold on;
        plot(psth_time, psth_large, 'm', 'LineWidth', 1.5);
        hold on;
        legend({'small', 'regular', 'large'}, 'Location', 'eastoutside');
        hold on;
        axis square
        %ylim([minv maxv])
        xlabel('Time to Lick');
        ylabel('amp');
        hold on;
        title({'Reward'; titlestats_regular_small; titlestats_regular_large; titlestats_large_small})
        %hold on;
        %annotation('textbox',[0.003 0 0.6 0.6],'String',{titlestats_regular_small; titlestats_regular_large; titlestats_large_small},'EdgeColor', "none",'FitBoxToText','on', 'FontSize', 10);
        %subtitle(subtitleStruct, 'FontSize', 7);
        hold on;
        
       
        hold on;
        txt=sprintf('Subject ID: %d - roi number uid: %d - roi number: %d - Session: %d', row_data.subject_id, row_uid.roi_number_uid, row_data.roi_number, row_data.session);
        sgtitle(txt);
        % Save the figure as JPG
        save_name = sprintf('Subject_%d_roi_number_%d_Session_%d.jpg', row_data.subject_id, row_data.roi_number, row_data.session);
        save_path = fullfile(save_dir, save_name);
        saveas(gcf, save_path, 'jpg');

        % Hold off to start a new plot in the next iteration
        hold off;
    end
end
