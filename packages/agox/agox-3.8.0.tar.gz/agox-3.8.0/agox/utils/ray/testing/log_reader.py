import re
from pathlib import Path

def convert_to_seconds(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

class LogReader():

    def __init__(self, log_file: Path):
        self.log_file = log_file.resolve()
        if self.log_file.exists():
            self.events, self.slurm_env = self.analyze_log(log_file)
            self.log_read = True
        else: 
            self.log_read = False

    def find_timestamp(self, line: str):
        try:
            time = re.findall('\d{2}:\d{2}:\d{2}', line)[0]
        except:
            time = False
        return time

    def analyze_log(self, log_file: Path):

        slurm_env = {}
        events = {}

        with open(log_file, 'r') as f:
            lines = f.readlines()

            for line in lines:
                time = self.find_timestamp(line)

                if time is False:
                    continue
                
                try:
                    split_line = line.split(' - ')
                    output = split_line[1]
                except: 
                    continue

                if 'SLURM' in output:
                    
                    split_line = output.split(':')
                    key, value = split_line[0], split_line[1]
                    key = key.strip()
                    value = value.strip()
                    if len(value) > 0:
                        slurm_env[key] = value


                if 'Event' in output:

                    event_index = int(re.findall('\d', output)[0])
                    events[event_index] = (time, output.strip())

            return events, slurm_env

    def get_out_path(self):
        """
        Not super robust.
        """
        directory = self.slurm_env['SLURM_SUBMIT_DIR']
        array_id = self.slurm_env['SLURM_ARRAY_TASK_ID']
        job_id = self.slurm_env['SLURM_ARRAY_JOB_ID']

        output_path=Path(directory, f"{array_id}/slurm-{job_id}-{array_id}.out")
        return output_path
    
    def print_output(self):
        path = self.get_out_path()

        if path.exists():
            with open(path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    print(line.strip())
        
        else:
            print(f"Output file {path} not found.")

    def get_slurm_env_var(self, key):
        return self.slurm_env.get(key, None)

    def get_partition(self):
        return self.get_slurm_env_var('SLURM_JOB_PARTITION')
    
    def get_node(self):
        return self.get_slurm_env_var('SLURM_JOB_NODELIST')

    def get_state(self):
        return self.events.get(6, None) is not None
    
    def get_most_recent_event_index(self):
        return max(self.events.keys())
    
    def get_execution_time(self):                
        start_time = convert_to_seconds(self.events[0][0])
        end_time = convert_to_seconds(self.events[self.get_most_recent_event_index()][0])
        return end_time - start_time