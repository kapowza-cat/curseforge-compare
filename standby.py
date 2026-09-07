import subprocess
import elevate

def set_close(value):
    subprocess.run(f'powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION {value}')
    subprocess.run(f'powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION {value}')

if __name__ == '__main__':
    elevate.elevate(graphical=True)
    set_close(0)
    print('Window may now be closed')
    print('Now set to \'do nothing\'')
    a = input('Accept this prompt to switch to \'sleep\'')
    set_close(1)