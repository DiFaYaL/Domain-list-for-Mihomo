#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

# --- Пути в стиле itdoginfo, адаптированы под этот репозиторий ---
# Эти переменные задают БАЗОВЫЕ пути хранения итоговых файлов.
# Например uaDomainsOut = 'Ukraine/ukraine_inside_domain' создаст:
#   Ukraine/ukraine_inside_domain.lst
#   Ukraine/ukraine_inside_domain.yaml
#   Ukraine/ukraine_inside_domain.mrs
rusDomainsInsideOut = 'Russia/inside-raw'
rusDomainsOutsideOut = 'Russia/outside-raw'
uaDomainsOut = 'Ukraine/ukraine_inside_domain'
servicesOut = 'Services'

# --- Оставлено в стиле itdoginfo, но сейчас не используется ---
# rusDomainsInsideSrcSingle = 'src/Russia-domains-inside-single.lst'
# rusDomainsInsideCategories = 'Categories'
# rusDomainsInsideServices = 'Services'
# rusDomainsOutsideSrc = 'src/Russia-domains-outside.lst'
# uaDomainsSrc = 'src/Ukraine-domains-inside.lst'
# SUBNET_SERVICES = [
#     'discord', 'meta', 'twitter', 'telegram',
#     'cloudflare', 'hetzner', 'ovh', 'digitalocean',
#     'cloudfront', 'roblox', 'google_meet',
# ]

ROOT = Path(__file__).resolve().parent.parent


def lines_from_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f'Warning: input file not found: {filepath}', file=sys.stderr)
        return []

    result = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if '#' in line:
                line = line.split('#', 1)[0].strip()

            if line.startswith('DOMAIN-SUFFIX,'):
                line = line[len('DOMAIN-SUFFIX,'):]

            if line.startswith('+.'):
                line = line[2:]
            elif line.startswith('.'):
                line = line[1:]

            if line:
                result.append(line.lower())

    return result


def compile_mrs(domains, output_base_path, behavior='domain'):
    output_base_path = Path(output_base_path)
    output_base_path.parent.mkdir(parents=True, exist_ok=True)

    txt_path = output_base_path.with_suffix('.txt')
    yaml_path = output_base_path.with_suffix('.yaml')
    mrs_path = output_base_path.with_suffix('.mrs')
    lst_path = output_base_path.with_suffix('.lst')

  #  clean_domains = sorted(set(d.lstrip('.').lower() for d in domains if d.strip()))

    with lst_path.open('w', encoding='utf-8', newline='\n') as f:
        for d in clean_domains:
            f.write(f'{d}\n')

    with yaml_path.open('w', encoding='utf-8', newline='\n') as f:
        f.write('payload:\n')
        for d in clean_domains:
            f.write(f"  - '+.{d}'\n")

    with txt_path.open('w', encoding='utf-8', newline='\n') as f:
        for d in clean_domains:
            f.write(f'+.{d}\n')

    try:
        subprocess.run(
            ['mihomo', 'convert-ruleset', behavior, 'text', str(txt_path), str(mrs_path)],
            check=True,
            cwd=ROOT,
        )
        print(f'Compiled: {mrs_path}')
    except subprocess.CalledProcessError as e:
        print(f'Compile error {txt_path}: {e}', file=sys.stderr)
        sys.exit(1)
   # finally:
   #     txt_path.unlink(missing_ok=True)


# --- Ниже намеренно оставлены куски itdoginfo, но они сейчас НЕ используются ---
# --- Они закомментированы, чтобы было видно отличие от исходного конвертора ---

# import tldextract
# import urllib.request
# import re
# import json
# import os
# import shutil
#
# ExcludeServices = {
#     'telegram.lst', 'cloudflare.lst', 'google_ai.lst', 'google_play.lst',
#     'hetzner.lst', 'ovh.lst', 'digitalocean.lst', 'cloudfront.lst',
#     'hodca.lst', 'roblox.lst', 'google_meet.lst'
# }
#
#
# def collect_files(src):
#     files = []
#     for dir_path in src:
#         path = Path(dir_path)
#         if path.is_dir():
#             files.extend(f for f in path.glob('*') if f.name not in ExcludeServices)
#         elif path.is_file() and path.name not in ExcludeServices:
#             files.append(path)
#     return files
#
#
# def collect_domains(src, dot_prefix=True):
#     domains = set()
#     for f in collect_files(src):
#         if not f.is_file():
#             continue
#         with open(f, encoding='utf-8') as infile:
#             for line in infile:
#                 ext = tldextract.extract(line.rstrip())
#                 if not ext.suffix:
#                     continue
#                 if re.search(r'[^а-я\\-]', ext.domain):
#                     domains.add(ext.fqdn)
#                 elif not ext.domain:
#                     prefix = '.' if dot_prefix else ''
#                     domains.add(prefix + ext.suffix)
#     return domains
#
#
# def raw(src, out):
#     domains = sorted(collect_domains(src))
#     with open(f'{out}-raw.lst', 'w', encoding='utf-8', newline='\\n') as file:
#         for name in domains:
#             file.write(f'{name}\\n')
#
#
# def dnsmasq(src, out, remove={'google.com'}):
#     domains = sorted(collect_domains(src) - remove)
#     with open(f'{out}-dnsmasq-nfset.lst', 'w', encoding='utf-8', newline='\\n') as file:
#         for name in domains:
#             file.write(f'nftset=/{name}/4#inet#fw4#vpn_domains\\n')
#     with open(f'{out}-dnsmasq-ipset.lst', 'w', encoding='utf-8', newline='\\n') as file:
#         for name in domains:
#             file.write(f'ipset=/{name}/vpn_domains\\n')
#
#
# def clashx(src, out, remove={'google.com'}):
#     domains = sorted(collect_domains(src) - remove)
#     with open(f'{out}-clashx.lst', 'w', encoding='utf-8', newline='\\n') as file:
#         for name in domains:
#             file.write(f'DOMAIN-SUFFIX,{name}\\n')
#
#
# def kvas(src, out, remove={'google.com'}):
#     domains = sorted(collect_domains(src, dot_prefix=False) - remove)
#     with open(f'{out}-kvas.lst', 'w', encoding='utf-8', newline='\\n') as file:
#         for name in domains:
#             file.write(f'{name}\\n')
#
#
# def mikrotik_fwd(src, out, remove={'google.com'}):
#     domains = sorted(collect_domains(src) - remove)
#     with open(f'{out}-mikrotik-fwd.lst', 'w', encoding='utf-8', newline='\\n') as file:
#         for name in domains:
#             if name.startswith('.'):
#                 file.write(f'/ip dns static add name=*.{name[1:]} type=FWD address-list=allow-domains forward-to=localhost\\n')
#             else:
#                 file.write(f'/ip dns static add name={name} type=FWD address-list=allow-domains match-subdomain=yes forward-to=localhost\\n')
#
#
# def compile_srs(data, name, json_dir='JSON', srs_dir='SRS'):
#     import json
#     import os
#     os.makedirs(json_dir, exist_ok=True)
#     os.makedirs(srs_dir, exist_ok=True)
#
#     json_path = os.path.join(json_dir, f'{name}.json')
#     srs_path = os.path.join(srs_dir, f'{name}.srs')
#
#     with open(json_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4)
#
#     try:
#         subprocess.run(
#             ['sing-box', 'rule-set', 'compile', json_path, '-o', srs_path], check=True
#         )
#         print(f'Compiled: {srs_path}')
#     except subprocess.CalledProcessError as e:
#         print(f'Compile error {json_path}: {e}', file=sys.stderr)
#         sys.exit(1)
#
#
# def srs_rule(name, rules):
#     compile_srs({'version': 3, 'rules': rules}, name)
#
#
# def generate_srs_for_categories(directories):
#     import os
#     exclude = {'meta', 'twitter', 'discord', 'telegram', 'hetzner', 'ovh', 'digitalocean', 'cloudfront', 'roblox', 'google_meet'}
#     for directory in directories:
#         for filename in os.listdir(directory):
#             if any(keyword in filename for keyword in exclude):
#                 continue
#             file_path = os.path.join(directory, filename)
#             if os.path.isfile(file_path):
#                 domains = lines_from_file(file_path)
#                 name = os.path.splitext(filename)[0]
#                 srs_rule(name, [{'domain_suffix': domains}])
#
#
# def prepare_dat_domains(domains, output_name, dirs=None):
#     import os
#     output_lists_directory = 'geosite_data'
#     os.makedirs(output_lists_directory, exist_ok=True)
#     domain_attrs = {domain: [] for domain in domains}
#
#     for directory in (dirs or []):
#         if not os.path.isdir(directory):
#             continue
#         for filename in os.listdir(directory):
#             file_path = os.path.join(directory, filename)
#             if not os.path.isfile(file_path):
#                 continue
#             attribute = os.path.splitext(filename)[0].replace('_', '-')
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 for line in f:
#                     domain = line.strip()
#                     if not domain:
#                         continue
#                     if domain in domain_attrs:
#                         domain_attrs[domain].append(f' @{attribute}')
#
#     output_file_path = os.path.join(output_lists_directory, output_name)
#     with open(output_file_path, 'w', encoding='utf-8') as out_f:
#         for domain, attrs in domain_attrs.items():
#             line = domain + ''.join(attrs)
#             out_f.write(f'{line}\\n')
#
#
# def prepare_dat_combined(dirs):
#     import os
#     import shutil
#     output_lists_directory = 'geosite_data'
#     os.makedirs(output_lists_directory, exist_ok=True)
#
#     for directory in dirs:
#         if not os.path.isdir(directory):
#             continue
#         for filename in os.listdir(directory):
#             source_path = os.path.join(directory, filename)
#             if not os.path.isfile(source_path):
#                 continue
#             new_name = os.path.splitext(filename)[0].replace('_', '-')
#             destination_path = os.path.join(output_lists_directory, new_name)
#             shutil.copyfile(source_path, destination_path)
#
#
# def parse_geosite_line(line):
#     from proto import geosite_pb2
#     parts = line.split()
#     raw_domain = parts[0]
#     attrs = [p.lstrip('@') for p in parts[1:] if p.startswith('@')]
#
#     if raw_domain.startswith('full:'):
#         domain_type = geosite_pb2.Domain.Full
#         value = raw_domain[5:]
#     elif raw_domain.startswith('regexp:'):
#         domain_type = geosite_pb2.Domain.Regex
#         value = raw_domain[7:]
#     elif raw_domain.startswith('keyword:'):
#         domain_type = geosite_pb2.Domain.Plain
#         value = raw_domain[8:]
#     else:
#         domain_type = geosite_pb2.Domain.RootDomain
#         value = raw_domain.lstrip('.')
#
#     return domain_type, value, attrs
#
#
# def generate_dat_domains(data_path='geosite_data', output_name='geosite.dat', output_directory='DAT'):
#     import os
#     from proto import geosite_pb2
#     os.makedirs(output_directory, exist_ok=True)
#     geo_site_list = geosite_pb2.GeoSiteList()
#
#     for filename in sorted(os.listdir(data_path)):
#         file_path = os.path.join(data_path, filename)
#         if not os.path.isfile(file_path):
#             continue
#
#         geo_site = geo_site_list.entry.add()
#         geo_site.country_code = filename.upper()
#
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if not line or line.startswith('#'):
#                     continue
#                 domain_type, value, attrs = parse_geosite_line(line)
#                 domain = geo_site.domain.add()
#                 domain.type = domain_type
#                 domain.value = value
#                 for attr in attrs:
#                     attribute = domain.attribute.add()
#                     attribute.key = attr
#                     attribute.bool_value = True
#
#     output_path = os.path.join(output_directory, output_name)
#     with open(output_path, 'wb') as f:
#         f.write(geo_site_list.SerializeToString())
#
#     print(f'Compiled .dat file: {output_path}')


if __name__ == '__main__':
    Path('Russia').mkdir(parents=True, exist_ok=True)
    Path('Ukraine').mkdir(parents=True, exist_ok=True)
    Path(servicesOut).mkdir(parents=True, exist_ok=True)

    # Russia inside
    russia_inside = lines_from_file(f'{rusDomainsInsideOut}.lst')
    if russia_inside:
        compile_mrs(russia_inside, rusDomainsInsideOut)

    # Russia outside
    russia_outside = lines_from_file(f'{rusDomainsOutsideOut}.lst')
    if russia_outside:
        compile_mrs(russia_outside, rusDomainsOutsideOut)

    # Ukraine inside
    ukraine_inside = lines_from_file(f'{uaDomainsOut}.lst')
    if ukraine_inside:
        compile_mrs(ukraine_inside, uaDomainsOut)

    # Services
    for service_file in sorted(Path(servicesOut).glob('*.lst')):
        domains = lines_from_file(service_file)
        if domains:
            compile_mrs(domains, service_file.with_suffix(''))
