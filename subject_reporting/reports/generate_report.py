from __future__ import unicode_literals

import jinja2
import os.path
import datetime
import string
import json
from subject_reporting import __version__ as version


class PartialFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        try:
            return super(PartialFormatter, self).get_value(key,args,kwargs)
        except (IndexError, KeyError):
            # Return the unformatted string
            return '{' + key + '}'
pf = PartialFormatter()

figures_dir = '{session}/figs'
report_dest = '/data/eeg/scalp/ltp/{experiment}/{subject}/{subject}_report.html'


def load_stats(subject, experiment):
    stat_dir = '/data/eeg/scalp/ltp/{experiment}/behavioral/stats'.format(experiment=experiment)
    data_file = os.path.join(stat_dir, 'stats_%s.json' % subject)
    if not os.path.exists(data_file):
        data_file = os.path.join(stat_dir, 'stats_%s_incomplete.json' % subject)
    with open(data_file, 'r') as f:
        stats = json.load(f)
    return stats


def build_report(subject, experiment, dest, **kwargs):

    sessions = load_stats(subject, experiment)['session']

    figures = dict(
        erp_plot=os.path.join(figures_dir, '{location}_erp.pdf'),
        spc=os.path.join(figures_dir, 'spc.pdf'),
        crp=os.path.join(figures_dir, 'crp.pdf'),
        pfr=os.path.join(figures_dir, 'pfr.pdf'),
        performance=pf.format(os.path.join(figures_dir, 'performance.pdf'), session=''),
    )
    env = jinja2.Environment(loader=jinja2.PackageLoader('subject_reporting.reports', 'templates'))
    template = env.get_template('{}.html'.format(experiment))
    kwargs.update(figures)
    report_str = template.render(
        datetime=datetime.datetime,
        subject=subject,
        experiment=experiment,
        sessions=sessions,
        **kwargs
    )
    with open(dest, 'w') as report:
        report.write(report_str)

if __name__ == '__main__':
    exp = 'ltpFR2'
    subj = input('Enter a subject ID: ')
    output_dest = report_dest.format(subject=subj, experiment=exp)
    build_report(subj, exp, output_dest,
                 # TODO: Add Javascript, CSS
                 js={},
                 css={},
                 version=version,
                 )