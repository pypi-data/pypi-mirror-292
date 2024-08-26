from .pip_deploy import push_to_pip


def app_release_deploy(version):
    '''
    
    '''
    # 1. Push to pip
    push_to_pip(version)

    # 2. Push to dockerhub (Not useful)



if __name__ == '__main__':
    print("Start Global deployment")
