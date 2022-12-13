from pywebio.input  import *
from pywebio.output import *
import configparser
from functools import partial
from pywebio import start_server
from pywebio.session import hold, info as session_info, register_thread,run_js,run_async

import util.dns
from util.dns import PROTO_UDP, PROTO_TCP, PROTO_TLS, PROTO_HTTPS, setup_signal_handler, flags_to_text
import re


@use_scope('file_input',clear=True)
def dns_server_upload():
    f = file_upload("Upload a file")
    f['filename'] = "dns-server.txt"
    open(f['filename'], 'wb').write(f['content'])

@use_scope('checker_output',clear=True)
def checker_output(data):
    count = 0
    output_list = list()
    put_processbar('dns_checker')
    with open("dns-server.txt") as file:
        fstring = file.readlines()

        for line in fstring:
            count+=1
            ip_addr = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", "{}".format(line))
            if ip_addr is not None:
                rsp = util.dns.ping(data['domain'], ip_addr[0], int(data['port']), data['DType'],
                                    int(data['wait_time']), int(data['count']), eval(data['proto']),
                                    src_ip=None, force_miss=data['edns'], want_dnssec=data['force_miss'])
                rsp.__dict__['DNS'] = ip_addr[0]
                output_list.append(rsp.__dict__)
                set_processbar('dns_checker', int(count) / int(len(fstring)))
    clear('checker_output')

    put_table(output_list,
                  header=["r_avg", "r_min", "r_max", "r_stddev", "r_lost_percent", "flags", "ttl","DNS"])
@use_scope('checker_form',clear=True)
def dns_checker():
    try:
        data = input_group("DNS Checker Form",
                           [input('Domain', name='domain', required=True),
                            radio('DST Port', name='port', options=["53", "80","443","853"], required=True),
                            radio('Data Type', name='DType', options=["A", "AAAA", "CNAME","NS"], required=True),
                            input('Wait Time', name='wait_time', type=NUMBER, required=True),
                            input('Count', name='count', type=NUMBER, required=True),
                            radio('Protocol',name='proto',options=["PROTO_UDP","PROTO_TCP", "PROTO_TLS","PROTO_HTTPS"], required=True),
                            radio('Use Edns', name='edns', options=["True", "False"], required=True),
                            radio('Force Miss', name='force_miss', options=["True", "False"], required=True),
                            radio('Want Dnssec', name='want_dnssec', options=["True", "False"], required=True)])

        checker_output(data)


    except:
            toast("DNS Checker Failed", color='warning')
            raise Exception("customer form failed")


@use_scope(clear=True)
def button_manager(btn):

    manager_list = {
        'DNS File Upload': dns_server_upload,
        'DNS CHECK': dns_checker
    }

    manager_list[btn]()

def main():

        put_markdown('## DNS Checker')
        put_markdown('> Yellow Team')
        put_buttons(['DNS File Upload', 'DNS CHECK'], onclick=button_manager)
        clear('file_input')
        hold()

if __name__ == '__main__':
    start_server(main, debug=True, port=8080, cdn=False)