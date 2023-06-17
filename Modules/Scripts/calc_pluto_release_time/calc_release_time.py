from datetime import datetime

record_file = '201701_release.txt'
log_file = 'jzhang14_201701.log'
log_file_odm88 = 'jzhang14_201701_odm88.log'

need_info = []
no_need_info = []
baseline_map = {}
with open(log_file, 'r') as log_input:
    for line in log_input.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        time_str, sh, info, msg = line.split(' | ')
        if msg.startswith('Starting...') or msg.startswith('Done...') or msg.startswith('Clearing existing'):
            dt = datetime.strptime(time_str, '%a %b %d %H:%M:%S PST %Y')
            # print '{} | {} | {}'.format(time_str, dt, msg)
            need_info.append(line)
            if msg.startswith('Starting...'):
                start_time = dt
                continue
            if msg.startswith('Clearing existing'):
                msg = msg.strip()
                tmp_data = msg.split('/')
                baseline = tmp_data[6]
                if baseline in baseline_map and baseline_map[baseline] != start_time:
                    print '{} already in map with value {}: , starting_time {}'.format(
                        baseline, baseline_map[baseline], start_time
                    )
                else:
                    baseline_map[baseline] = start_time
                continue

        else:
            no_need_info.append(line)

with open(log_file_odm88, 'r') as log_input:
    for line in log_input.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        time_str, sh, info, msg = line.split(' | ')
        if msg.startswith('Starting...') or msg.startswith('Done...') or msg.startswith('Clearing existing'):
            dt = datetime.strptime(time_str, '%a %b %d %H:%M:%S PST %Y')
            # print '{} | {} | {}'.format(time_str, dt, msg)
            need_info.append(line)
            if msg.startswith('Starting...'):
                start_time = dt
                continue
            if msg.startswith('Clearing existing'):
                msg = msg.strip()
                tmp_data = msg.split('/')
                baseline = tmp_data[5]
                if baseline in baseline_map and baseline_map[baseline] != start_time:
                    print '{} already in map with value {}: , starting_time {}'.format(
                        baseline, baseline_map[baseline], start_time
                    )
                else:
                    baseline_map[baseline] = start_time
                continue

        else:
            no_need_info.append(line)


# print baseline_map

with open(record_file, 'r') as record_input:
    print "============================================"
    print 'Baseline\tStart Time\tRelease Hour\tDuration(hours)\tComponent Count\tHas RPDS\tHas RLDS\tComponents'
    for line in record_input.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        # print line

        baseline, ts, count, components = line.split('\t')
        release_time = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')

        # print '{} | {} | {} | {} | {}'.format(baseline, ts, release_time, count, components)

        if baseline in baseline_map:
            start_time = baseline_map[baseline]
            delta = release_time - start_time
            # hour = int(delta.total_seconds() / 3600)
            # minutes = int((delta.total_seconds() - hour * 3600) / 60)
            # duration = '{}:{}'.format(hour, minutes)
            duration = round(delta.total_seconds() / 3600, 2)
            # print delta, duration
        else:
            start_time = None
            duration = None
        # print '{}\t{}\t{}\t{}\t{}\t{}'.format(baseline, start_time, release_time, duration, count, component
        has_rpds = 'riskplanningdecisionserv' in components
        has_rlds = 'risklitedecisionserv' in components

        if duration is None \
                or duration > 48 \
                or (int(count) <= 2):
            continue

        print '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            baseline,
            start_time,
            release_time,
            duration,
            count,
            int(has_rpds),
            int(has_rlds),
            components
        )
