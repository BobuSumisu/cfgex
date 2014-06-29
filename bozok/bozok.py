#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import argparse
import re
import json
import struct
import os

RE_VERSION = re.compile(b'CFG\x00((?:[0-9]\x00(?:\.\x00)?)+)\x00\00')
PACKAGEINFO = 'P\x00A\x00C\x00K\x00A\x00G\x00E\x00I\x00N\x00F\x00O\x00\x00\x00'

def extract_version(data):
  m = RE_VERSION.search(data)
  if not m:
    raise Exception('Version not found.')
  version = m.group(1).replace('\x00', '')
  if version != '1.0':
    return version
  else:
    if data.find('m\x00y\x00p\x00a\x00s\x00s\x00') == -1:
      return version + 'a'
    else:
      return version + 'b'
  
  
def extract_config(data):
  version = extract_version(data)
  config_index = data.find(PACKAGEINFO)
  config_data = data[config_index + len(PACKAGEINFO):]
  config_index += len(PACKAGEINFO)
  
  if version == '1.0a':
    unpacked = struct.unpack('<255s100s100s100s100sicc', config_data[:661])
    return {
      'version': version,
      'ips': unpacked[0].replace('\x00', '').encode('string_escape'),
      'exe_name': unpacked[1].replace('\x00', '').encode('string_escape'),
      'reg_key': unpacked[2].replace('\x00', '').encode('string_escape'),
      'server_id': unpacked[3].replace('\x00', '').encode('string_escape'),
      'mutex_name': unpacked[4].replace('\x00', '').encode('string_escape'),
      'port': unpacked[5],
      'install_exe': unpacked[6] == '\x01',
      'install_reg': unpacked[7] == '\x01',
      'extension': 'bozplugin.dll'
    }  
  elif version == '1.0b':
    unpacked = struct.unpack('<255s100s100s100s100s100sicc', config_data[:761])
    return {
      'version': version,
      'ips': unpacked[0].replace('\x00', '').encode('string_escape'),
      'exe_name': unpacked[1].replace('\x00', '').encode('string_escape'),
      'reg_key': unpacked[2].replace('\x00', '').encode('string_escape'),
      'server_id': unpacked[3].replace('\x00', '').encode('string_escape'),
      'mutex_name': unpacked[4].replace('\x00', '').encode('string_escape'),
      'password': unpacked[5].replace('\x00', '').encode('string_escape'),
      'port': unpacked[6],
      'install_exe': unpacked[7] == '\x01',
      'install_reg': unpacked[8] == '\x01',
      'extension': 'bozplugin.dll'
    }
  else:
    config_len = config_data.find('\x00\x00')
    config_data = config_data[:config_len]
    config_string = config_data.replace('\x00', '')
    config_fields = config_string.split('|')
    if len(config_fields) < 12:
      return None
    config_fields[12] = filter(None, config_fields[12].split('*'))
    
    if len(config_fields) < 13:
      return {
        'server_id': config_fields[0].encode('string_escape'),
        'mutex_name': config_fields[1],
        'exe_name': config_fields[2],
        'reg_key': config_fields[3],
        'extension': config_fields[4],
        'password': config_fields[5],
        'flag_install': config_fields[6] == '1',
        'flag_persist': config_fields[7] == '1',
        'flag_visible_mode': config_fields[8] == '1',
        'flag_unknown_1': config_fields[9] == '1',
        'flag_unknown_2': config_fields[10] == '1',
        'port': int(config_fields[11]),
        'ips': config_fields[12]
      }
    else:
      return {
        'server_id': config_fields[0].encode('string_escape'),
        'mutex_name': config_fields[1],
        'exe_name': config_fields[2],
        'reg_key': config_fields[3],
        'extension': config_fields[4],
        'password': config_fields[5],
        'flag_install': config_fields[6] == '1',
        'flag_persist': config_fields[7] == '1',
        'flag_visible_mode': config_fields[8] == '1',
        'flag_unknown_1': config_fields[9] == '1',
        'flag_unknown_2': config_fields[10] == '1',
        'port': int(config_fields[11]),
        'ips': config_fields[12],
        'flag_unknown_3': config_fields[13] == '1'
      }

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--extract-config', action='store_true', help='extract and output bozok config')
  parser.add_argument('-v', '--extract-version', action='store_true', help='extract and output bozok version')
  parser.add_argument('-r', '--recursive', action='store_true', help='treat INFILE as a directory and run recursively')
  parser.add_argument('-s', '--statistics', action='store_true', help='used with --recursive to get some statistics')
  parser.add_argument(dest='infile', metavar='INFILE', help='bozok executable')
  args = parser.parse_args()
  
  if args.recursive:
    stats = { 'total': 0, 'failed': 0, 'extracted': 0 }
    for dir,subdir,filenames in os.walk(args.infile):
      for filename in filenames:
        stats['total'] += 1
        data = open(os.path.join(dir, filename), 'rb').read()
        try:
          version = extract_version(data)
          if version not in stats:
            stats[version] = 0
          stats[version] += 1
          config = extract_config(data)
          if not config:
            raise Exception()
          stats['extracted'] += 1
        except:
          stats['failed'] += 1
          continue
         
        if args.extract_version:
          print version
        if args.extract_config:
          print json.dumps(config, indent=2, sort_keys=True)
         
    if args.statistics:
      print json.dumps(stats, indent=2, sort_keys=True)
  else:
    try:
      data = open(args.infile, 'rb').read()
      version = extract_version(data)
      config = extract_config(data)
    
      if args.extract_version:
        print version
      if args.extract_config:
        print json.dumps(config, indent=2, sort_keys=True)

    except Exception as e:
      print 'Failed: ' + str(e)