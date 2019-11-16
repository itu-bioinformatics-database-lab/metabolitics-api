

from __future__ import absolute_import


import os
import yaml
import logging.config

from subprocess import call
import click
import os
import uuid
import json
from collections import defaultdict
import pickle
from sklearn.pipeline import  Pipeline
from app.app import app
from app.models import db
from sklearn_utils.utils import SkUtilsIO
from metabolitics.preprocessing import *
from metabolitics.utils import load_network_model

@click.group()
def cli():
    pass


@cli.command()
def run_api():
    app.run(
        host=os.environ.get('HOST', 'localhost'),
        debug=True
        # os.environ.get('DEBUG', True)
    )


@cli.command()
def run_celery():
    call('celery -A app.celery worker')
    # celery4 = make_celery(app)
    # call('celery -A app.celery2.celery worker -l info -Q celery')

    # call('celery --app =app worker --loglevel=info')
    # make_celery(app)


@cli.command()
def migrate():
    db.create_all()


@cli.command()
def generate_secret():
    with open('../secret.txt', 'w') as f:
        f.write(str(uuid.uuid4()))


@cli.command()
def generate_angular_friendly_model():
    '''
    This function convert json model into angular friendly json
    '''
    model = load_network_model()
    model_json = json.load(open('../dataset/network/recon2.json'))

    reactions, metabolites = model_json['reactions'], model_json['metabolites']
    model_json = defaultdict(dict)
    model_json['pathways'] = defaultdict(list)

    for m in metabolites:
        m['reactions'] = [
            r.id for r in model.metabolites.get_by_id(m['id']).reactions
        ]
        model_json['metabolites'][m['id']] = m

    for r in reactions:
        # r['gene_reaction_rule'], r['notes'] = [], {}
        del r['gene_reaction_rule']
        del r['notes']

        model_json['reactions'][r['id']] = r
        model_json['pathways'][r.get('subsystem', 'NOpathway')].append(r['id'])

    json.dump(model_json, open('../outputs/ng-recon.json', 'w'))



@cli.command()
def healties_model():
    disease_name = 'BC'
    path = '../datasets/diseases/%s.csv' % disease_name
    X, y = SkUtilsIO(path).from_csv(label_column='stage')
    y = ['bc' if i != 'h' else 'healthy' for i in y]

    pipe = MetaboliticsPipeline([
        # 'metabolite-name-mapping-toy',
        # 'metabolite-name-mapping',
        'naming-toy',
        'fold-change-scaler',
    ])
    X_t = pipe.fit_transform(X, y)

    model = Pipeline([
        ('metabolitics-transformer', MetaboliticsTransformer(n_jobs=1)),
        ('reaction-diff', ReactionDiffTransformer())
    ])
    # model = MetaboliticsPipeline([
    #     'metabolitics-transformer',
    #     'reaction-diff',
    # ])
    model.fit(X_t, y)
    with open('../models/api_model.p', 'wb') as f:
        pickle.dump(model, f)


if __name__ == '__main__':
    cli()
# cli()
