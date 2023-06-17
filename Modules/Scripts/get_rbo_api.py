import requests
import os.path
import sys
import getopt


# update at 2019-08-07
# http://nexus.paypal.com/nexus/service/local/*  does not work now as per artifactory team.
# Please use http://nexus.paypal.com/nexus/content/repositories/releases/com/paypal/compliance/compliance-common-constant/3.0.102/compliance-common-constant-3.0.102.jar

def get_rbo_jar(version, file_type='jar', folder=None):
    # url_tpl = 'https://engineering.paypalcorp.com/nexus/service/local/artifact/maven/redirect?r=releases&g=com.paypal.risk.idi&a=rbo-api&v={}&e=jar'
    # url_tpl = 'https://nexus.paypal.com/artifactory/releases/com/paypal/risk/idi/rbo-api/{version}/'
    url_tpl = 'http://paypalcentral.es.paypalcorp.com/artifactory/releases/com/paypal/risk/idi/rbo-api/{version}/'
    url = url_tpl.format(version=version)

    if file_type == 'source':
        file_name = 'rbo-api-{}-sources.jar'.format(version)
    else:
        file_name = 'rbo-api-{}.jar'.format(version)
    url += file_name

    if folder is not None:
        file_name = os.path.join(folder, file_name)

    ret = requests.get(url)
    if ret.status_code != 200:
        print('Error calling {}'.format(url))
        return
    with open(file_name, 'wb') as jar_file:
        jar_file.write(ret.content)
        print('Get {} successfully'.format(file_name))


def usage():
    print('Usage:%s -v {version} [-s] [-f {folder}]' % sys.argv[0])


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(1)
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], '[v:sf:]', [''])
            print('{} {}'.format(opts, args))

            version = None
            jar_type = None
            folder = None
            for opt, arg in opts:
                if opt == '-v':
                    version = arg
                elif opt == '-s':
                    jar_type = 'source'
                elif opt == '-f':
                    folder = arg
                else:
                    print('wrong opt')

            if version is not None:
                get_rbo_jar(version, 'jar', folder)
                if jar_type is not None:
                    get_rbo_jar(version, jar_type, folder)

            else:
                usage()
                sys.exit(1)

        except getopt.GetoptError:
            print('getopt error!')
            usage()
            sys.exit(1)
