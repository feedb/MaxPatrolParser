#!/usr/bin/env python
import xml.etree.ElementTree as ET
import csv

namespaces = {'PT': 'http://www.ptsecurity.ru/reports'}
protocols = {'6': 'TCP', '17': 'UDP'}
port_status = {'0': 'open', '1': 'locked', '2': 'unavailable'}


def mp_parse(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    host_info = []
    for host in root.findall('./PT:data/PT:host', namespaces):
        ip = host.attrib['ip']
        for soft in host.findall('PT:scan_objects/PT:soft', namespaces):
            appended_info = list()
            appended_info.append(ip)
            # finds soft name
            try:
                appended_info.append(soft.find('PT:banner/PT:table/PT:body/PT:row/PT:field', namespaces).text)
            except:
                appended_info.append(None)
            try:
                appended_info.append(soft.attrib['port'])
            except:
                appended_info.append(None)
            try:
                appended_info.append(protocols[soft.attrib['protocol']])
            except:
                appended_info.append(None)
            try:
                appended_info.append(port_status[soft.attrib['port_status']])
            except:
                appended_info.append(None)
            # finds cve and cvss if exists, else sets None
            vuln_finder(appended_info, root, soft)
            host_info.append(appended_info)
    return host_info


def vuln_finder(appended_info, root, soft):
    for vulnerabilty in soft.findall('PT:vulners/PT:vulner', namespaces):
        for vuln in root.findall('./PT:vulners/PT:vulner', namespaces):
            if vuln.attrib['id'] == vulnerabilty.attrib['id']:
                try:
                    appended_info.append(vuln.find('PT:cvss', namespaces).attrib['base_score'])
                except:
                    appended_info.append(None)
                try:
                    appended_info.append(vuln.find('PT:global_id', namespaces).attrib['value'])
                except:
                    appended_info.append(None)
                try:
                    appended_info.append(vuln.find('PT:description', namespaces).text)
                except:
                    appended_info.append(None)


if __name__ == '__main__':
    res = mp_parse('test.xml')
    with open('test.csv', 'w', newline='') as file:
        wr = csv.writer(file, quoting=csv.QUOTE_ALL)
        wr.writerows(res)
