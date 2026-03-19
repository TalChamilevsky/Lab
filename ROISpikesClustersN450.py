import datajoint as dj
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from scipy.stats import zscore
from scipy.cluster.hierarchy import linkage, fcluster

schema = dj.schema("talch012_lick2d")

@schema
class ROISpikesClustersN450(dj.Computed):
    definition = """
    # Per-ROI cluster assignment — global hierarchical clustering (N<=450/area, all subjects/sessions/areas)
    -> lick2dtal.ROILick2DPSTHSpikes3
    ---
    cluster_id                           : int   # assigned cluster label (1 … total_k_clusters)
    total_k_clusters                     : int   # total K used for this run (e.g. 25)
    cells_per_subject_session_brain_area : int   # ROIs from same subject x session x brain_area that passed filtering
    """

    def make(self, key):
        # ── 1. fetch all data globally ────────────────────────────────────────
        rel_ROI   = img.ROI - img.ROIBad
        brainarea = img.ROIBrainArea & rel_ROI
        combined  = (lick2dtal.ROILick2DPSTHSpikes3
                     * brainarea
                     * exp2.SessionBehavioral
                     * lick2dtal.ROILick2DPSTHStatsSpikes3
                     - img.Volumetric)

        fetch_all = combined.fetch(as_dict=True)

        # ── 2. sample and normalise ───────────────────────────────────────────
        normalized_psth_regular = []
        unique_subject_id  = np.unique([table['subject_id']                for table in fetch_all])
        unique_brain_areas = np.unique([table['brain_area']                for table in fetch_all])
        unique_session_b   = np.unique([table['behavioral_session_number'] for table in fetch_all])

        cells_per_brain_area = 450
        sampled_cells_count  = {area: 0 for area in unique_brain_areas}
        missing_brain_areas  = defaultdict(list)

        for subject_id in unique_subject_id:
            for behavioral_session in unique_session_b:
                num_samples_subject_id = 0

                for brain_area in unique_brain_areas:
                    filter_data = [table for table in fetch_all if
                                   (table['brain_area']                    == brain_area) and
                                   (table['behavioral_session_number']     == behavioral_session) and
                                   (table['subject_id']                    == subject_id) and
                                   (table['psth_regular_odd_vs_even_corr'] > 0.5) and
                                   (table['psth_small_odd_vs_even_corr']   > 0.5) and
                                   (table['brain_area'] not in
                                    ['SSp-n', 'SSp-m', 'VISa', 'VISam', 'VISrl'])]

                    if not filter_data:
                        missing_brain_areas[(subject_id, behavioral_session)].append(brain_area)
                    else:
                        sampled_indices = np.random.choice(
                            len(filter_data),
                            size=min(cells_per_brain_area, len(filter_data)),
                            replace=False
                        )

                        for idx in sampled_indices:
                            data_entry = filter_data[idx]

                            psth_regular12  = np.frombuffer(data_entry['psth_regular'], dtype=np.float32)[:14]
                            path_large_data = np.frombuffer(data_entry['psth_large'],   dtype=np.float32)[:14]
                            psth_small_data = np.frombuffer(data_entry['psth_small'],   dtype=np.float32)[:14]
                            psth_regular1   = np.concatenate([psth_regular12, path_large_data, psth_small_data])

                            max_value  = np.max(psth_regular12)
                            modulation = ((max_value - np.min(psth_regular12)) / max_value) * 100

                            if modulation > 25:
                                norm_now = zscore(psth_regular1)

                                entry_dict = {
                                    # original grouping fields
                                    'subject_id':                subject_id,
                                    'brain_area':                brain_area,
                                    # all PKs from data_entry
                                    'session':                   data_entry['session'],
                                    'session_epoch_type':        data_entry['session_epoch_type'],
                                    'session_epoch_number':      data_entry['session_epoch_number'],
                                    'fov_num':                   data_entry['fov_num'],
                                    'plane_num':                 data_entry['plane_num'],
                                    'channel_num':               data_entry['channel_num'],
                                    'roi_number':                data_entry['roi_number'],
                                    'behavioral_session_number': data_entry['behavioral_session_number'],
                                    'normalized_data':           norm_now.tolist()
                                }

                                normalized_psth_regular.append(entry_dict)
                                sampled_cells_count[brain_area] += 1

                # print missing brain areas per subject x session
                for (sid, bsess), missing_areas in missing_brain_areas.items():
                    if missing_areas:
                        print(f"Missing brain areas for Subject ID {sid}, "
                              f"Session {bsess}: {missing_areas}")
                print(f"Subject ID: {subject_id}, Number of Samples: {num_samples_subject_id}")

        print(f"[ROISpikesClustersN450] {len(normalized_psth_regular)} ROIs passed filtering "
              f"out of {len(fetch_all)} total.")

        # ── 3. clustering ─────────────────────────────────────────────────────
        num_clusters    = 25
        metric          = 'euclidean'
        method          = 'ward'
        normalized_data = np.array([e['normalized_data'] for e in normalized_psth_regular])

        linkage_matrix = linkage(normalized_data, method=method, metric=metric)
        cluster_labels = fcluster(linkage_matrix, num_clusters, criterion='maxclust')

        # ── 4. plot cluster averages ──────────────────────────────────────────
        cluster_averages = []
        cluster_sizes    = []
        for i in range(1, num_clusters + 1):
            cluster_data = normalized_data[cluster_labels == i]
            cluster_averages.append(np.mean(cluster_data, axis=0))
            cluster_sizes.append(cluster_data.shape[0])

        sorted_indices          = np.argsort(cluster_sizes)[::-1]
        sorted_cluster_averages = [cluster_averages[i] for i in sorted_indices]
        sorted_cluster_sizes    = [cluster_sizes[i]    for i in sorted_indices]

        num_rows = int(np.ceil(num_clusters / 5))
        fig, axes = plt.subplots(num_rows, 5, figsize=(20, 4 * num_rows))
        axes = axes.flatten()
        colors = ['blue', 'orange', 'green']

        for i, (avg, size) in enumerate(zip(sorted_cluster_averages, sorted_cluster_sizes)):
            ax = axes[i]
            part1, part2, part3 = avg[:14], avg[14:28], avg[28:42]
            x_indices = np.arange(14)
            ax.plot(x_indices, part1, color=colors[0], label='Regular')
            ax.plot(x_indices, part2, color=colors[1], label='Large')
            ax.plot(x_indices, part3, color=colors[2], label='Small')
            ax.set_title(f'Cluster {sorted_indices[i] + 1}\nSize: {size}')
            ax.set_xlabel('Time')
            ax.set_ylabel('Activity (norm.)')
            ax.legend()

        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

        # ── 5. bulk insert only the clustered subset ──────────────────────────
        cells_count = Counter(
            (e['subject_id'], e['behavioral_session_number'], e['brain_area'])
            for e in normalized_psth_regular
        )

        rows = [
            {
                'subject_id':                          entry['subject_id'],
                'session':                             entry['session'],
                'session_epoch_type':                  entry['session_epoch_type'],
                'session_epoch_number':                entry['session_epoch_number'],
                'fov_num':                             entry['fov_num'],
                'plane_num':                           entry['plane_num'],
                'channel_num':                         entry['channel_num'],
                'roi_number':                          entry['roi_number'],
                'cluster_id':                          int(cluster_id),
                'total_k_clusters':                    num_clusters,
                'cells_per_subject_session_brain_area': cells_count[
                    (entry['subject_id'],
                     entry['behavioral_session_number'],
                     entry['brain_area'])
                ],
            }
            for entry, cluster_id in zip(normalized_psth_regular, cluster_labels)
        ]

        self.insert(rows, skip_duplicates=True, allow_direct_insert=True)
        print(f"[ROISpikesClustersN450] Inserted {len(rows)} clustered ROIs "
              f"({len(fetch_all) - len(rows)} filtered out / not clustered).")


# ── run once directly — do not use populate ───────────────────────────────────
ROISpikesClustersN450().make(key={})