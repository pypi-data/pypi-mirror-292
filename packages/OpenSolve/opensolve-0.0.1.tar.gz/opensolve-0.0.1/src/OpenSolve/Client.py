import requests
import os
import datetime
from randomNames import randName
chunk_size = 5*1024    

class client:
    def __init__(self, usr, tkn):
        self.username = usr
        self.token = tkn
        self.osapi_url = 'https://api.open-solve.com' 
        self.latest_job_hash = None
        self.headers = {'username': self.username, 'token': self.token}

    def find_hash(self, job_hash = None):
        if job_hash is None and self.latest_job_hash is None:
            raise ValueError('Could not find a job to check')
        elif job_hash is None and self.latest_job_hash is not None:
            jh = self.latest_job_hash
        else:
            jh = job_hash
        return jh

    def submit_job(self, problem_file, warmstart_file=None, options_file=None,
                   mem_limit = None, time_limit = None, job_name = None):
        # problem_file: str; path to problem file
        # warmstart_file: str; path to warmstart solution/basis file
        # options_file: str; path to options file for HiGHS options
        # mem_limit: int; number of Gibs of RAM to limit the job to
        # time_limit: int; number of seconds to limit job runtime to

        # error handling on inputs
        if not isinstance(problem_file,str) or not os.path.isfile(problem_file):
            raise ValueError(f'problem_file must be a path to an existing file; given: {problem_file}')
        if warmstart_file is not None and \
                    (not isinstance(warmstart_file,str) or \
                        not os.path.isfile(warmstart_file)):
            raise ValueError(f'warmstart_file must be a path to an existing file; given {warmstart_file}')
        if options_file is not None and \
                    (not isinstance(options_file, str) or \
                        not os.path.isfile(options_file)):
            raise ValueError(f'options_file must be path to an existing file; given {options_file}')
        if not isinstance(mem_limit, int) and mem_limit is not None:
            raise ValueError('mem_limit must be an integer')
        if not isinstance(time_limit, int) and time_limit is not None:
            raise ValueError('mem_limit must be an integer')
        

        if problem_file.split('.')[-1] not in ['lp', 'mps', 'ems']:
            raise ValueError('Problem file must be of type .lp, .mps, or .ems')

        if job_name is None:
            job_name = randName()
        
        self.job_name = job_name
        

        job_data = {'p_file': problem_file.split('.')[-1]}
         
        if mem_limit is not None:
            job_data['mem_lim'] = mem_limit
        else:
            job_data['mem_lim'] = ''
        
        self.mem_lim = job_data['mem_lim']

        if time_limit is not None:
            job_data['time_lim'] = time_limit
        else:
            job_data['time_lim'] = ''
        
        self.time_lim = job_data['time_lim']

        if options_file is not None:
            job_data['options'] = 'txt'
        
        if warmstart_file is not None:
            job_data['rsf'] = 'sol'

        # post job meta-data
        r = requests.post(self.osapi_url + '/receive', data = job_data, 
            headers={'token':self.token, 'username':self.username})

        if r.status_code != 200:
            raise ValueError(f"Job not acknowledged: {r.text}")
        
        job_dict = r.json()

        # accepted job receives job_hash
        self.latest_job_hash = job_dict['job_hash']
        
        # FIGURE OUT CHECKSUMS FOR THE FOLLOWING UPLOADS
        try:
            queue_data = self.upload_files(job_dict, problem_file, warmstart_file,
                options_file)
        except Exception as err:
            print("File(s) not uploaded.")
            print(f"Unexpected {err=}, {type(err)=}")
            raise
        
        # queue job
        u = self.queue_job(queue_data)
        
        if u.status_code != 200:
            raise ValueError(f"Problem queueing job: {u.text}")
        
        # print(f"File(s) uploaded for job hash {self.latest_job_hash} ({job_name})")
        return (self.latest_job_hash, job_name)
            
    def upload_files(self, url_dict, problem_file, warmstart_file=None, 
                    options_file=None, job_hash = None):
        
        jh = self.find_hash(job_hash = job_hash)

        # problem file upload
        pfile = '.'.join([jh, problem_file.split('.')[-1]])
        
        with open(problem_file, 'r') as f:
            t = requests.put(url_dict['pfile'],
                            data = f.read(), stream=True)
        if t.status_code != 200:
            print(t.text)
            raise ValueError(t)
        data = {'pf_name': pfile}
        
        # options_file upload
        if options_file is not None:
            optf = '.'.join([jh, 'txt'])
            with open(options_file, 'r') as f:
                v = requests.put(url_dict['options'],
                                    data = f.read(), stream=True)
            if v.status_code != 200:
                print(v.text)
                raise ValueError(v)
            data['opt_name'] = optf
        
        # warmstart file upload
        if warmstart_file is not None:
            rsf = '.'.join([jh, 'sol'])
            with open(warmstart_file, 'r') as f:
                q = requests.put(url_dict['rsf'],
                                data = f.read(),
                                stream=True)
            if q.status_code != 200:
                print(q.text)
                raise ValueError(q)
            data['rsf_name'] = rsf
        
        data['job_hash'] = jh
        
        return data
        
    def queue_job(self, queue_data, job_hash = None):
        
        queue_data['job_name'] = self.job_name
        queue_data['mem_lim'] = self.mem_lim
        queue_data['time_lim'] = self.time_lim
        queue_data['username'] = self.username

        u = requests.post(self.osapi_url + '/queue', 
            data = queue_data,
            headers={'token':self.token, 'username':self.username}
        )
        # response will always be a string
        print(u.text)
        return u

        
    
    def check_job(self, job_hash = None):
        
        jh = self.find_hash(job_hash = job_hash)

        data = {'job_hash': jh}
        r = requests.post(self.osapi_url + '/status', data=data, 
                          headers={'token':self.token, 'username':self.username}
        )
        # return a dictionary
        return r.json()
    
    def pull_results(self, job_hash = None, file_types = 'all',
                    download_path = os.getcwd()):

        jh = self.find_hash(job_hash = job_hash)

        if file_types not in ['all', 'output', 'input']:
            print('Invalid file type passed to file_type; aborting retrieval.')
            return

        fprefix = {
            'all' : ['lf_name',
                    'sf_name',
                    'pf_name',
                    'opt_name',
                    'rsf_name'
            ],
            'output' : ['lf_name',
                    'sf_name'
            ],
            'input' : ['pf_name',
                    'opt_name',
                    'rsf_name'
            ]
        }

        rdat = self.check_job(job_hash=jh)
        
        if rdat['system_status'] != 'complete':
            print('No results to pull')
            return

        job_data = requests.post(self.osapi_url + '/pull_results',
                                 data = {'job_hash': jh},
                                 headers= {'username':self.username, 'token': self.token}
        )
        rdat = job_data.json()

        dks = []
        for k in rdat:
            if rdat[k] == 'unspecified' or rdat[k] == 'No_file':
                dks.append(k)
        
        for k in dks:
            del rdat[k]
        
        
        pf = rdat['pf_name']
        
        sfiles = [f for f in fprefix['all'] if f in rdat and f in fprefix[file_types]]

        rdata = {sfiles[i]: rdat[sfiles[i]] for i in range(len(sfiles))}
        rdata['job_hash'] = jh

        furls = requests.post(self.osapi_url + '/copy', 
            data = rdata,
            headers= {'username':self.username, 'token': self.token})

        furls_dict = furls.json()

        for f in furls_dict:
            match f:
                case 'lf_name':
                    save_name = '_'.join(['Job', jh, 'Logs']) + '.txt' 
                case 'sf_name':
                    save_name = '_'.join(['Job', jh, 'Solution']) + '.sol' 
                case 'pf_name':
                    save_name = '.'.join(['_'.join(['Job', jh, 'Problem']), 
                                    pf.split('.')[1]])
                case 'opt_name':
                    save_name = '_'.join(['Job', jh, 'Options']) + '.txt'
                case 'rsf_name':
                    save_name = '_'.join(['Job', jh, 'Warmstart']) + '.sol'

            rdat[f] = save_name

            r = requests.get(furls_dict[f], stream=True)
            with open(os.path.join(download_path,save_name), 'wb') as fd:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)
            
        return rdat

    def ls_jobs(self, category='active', date_limit=None):
        if category not in ['all', 'active', 'complete']:
            print('Error: category must be "all", "active", or "complete"')
            return
        if date_limit is not None:
            try:
                dl = datetime.datetime.strptime(
                    date_limit, 
                    '%Y-%m-%d'
                )
            except ValueError:
                print('Error: Valid dates must follow the format YYYY-MM-DD')
                return

            r = requests.post(self.osapi_url + '/jobs', 
                    data={'date_limit': date_limit,
                            'jobs': category},
                    headers = {'username': self.username, 'token': self.token}
            )
        else:
            r = requests.post(self.osapi_url + '/jobs',
                    data = {'jobs': category},
                    headers = {'username': self.username, 'token': self.token}
            )
        if r.status_code == 200:
            return r.json()
        else:
            raise ValueError(r.text)

