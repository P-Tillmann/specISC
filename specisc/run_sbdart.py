# -*- coding: utf-8 -*-

import subprocess
import pandas as pd
from io import StringIO

def generate_input(tcloud, albcon):
    input_str = f"""
 &INPUT
    idatm=4,
    isat=0,
    wlinf=.25,
    wlsup=1.0,
    wlinc=.005,
    iout=1,
    tcloud={tcloud}
    albcon={albcon}
 /
"""
    with open('INPUT', 'w') as file:
        file.write(input_str)
        return input_str


# Launch the Fortran binary as a subprocess


for i in range(100):
    print(i)

    generate_input(tcloud=5, albcon=0.2)
    
    proc = subprocess.Popen(['./sbdart'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    
    (out, err) = proc.communicate()
    
    # Read the output from the subprocess through its standard output stream
    #output_str = proc.stdout.readline().decode('utf-8')
    
    # Print the output
    #print(out)
    
    # Close the subprocess
    proc.stdin.close()
    proc.stdout.close()
    proc.wait()
    
    #df = pd.read_csv(StringIO(out.decode('utf-8')), sep="\s\s",  skiprows=3, header=None)
    #df.set_index(0).plot()
