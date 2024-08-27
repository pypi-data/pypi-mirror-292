"""test the session class"""
import os
import sys
import uuid
import subprocess as sp
import pytest
from virtmat.language.cli import run_model, run_session
from virtmat.language.interpreter.session import Session
from virtmat.language.utilities.textx import GRAMMAR_LOC


@pytest.fixture(name='model_file')
def model_file_fixture(tmp_path):
    """prepare a model file as a fixture"""
    path = os.path.join(tmp_path, 'model.vm')
    model = "a = 1; print(a)"
    with open(path, 'w', encoding='utf-8') as ifile:
        ifile.write(model)
    return path


@pytest.fixture(name='lpad_file')
def lpad_file_fixture(tmp_path, lpad):
    """launchpad file as fixture"""
    path = os.path.join(tmp_path, 'launchpad.yaml')
    lpad.to_file(path)
    return path


def test_script_direct_call_parse_clargs(capsys):
    """directly call the parse_clargs() function otherwise not covered"""
    msg = 'the following arguments are required: -f/--model-file'
    with pytest.raises(SystemExit, match='2'):
        run_model.parse_clargs()
    assert msg in capsys.readouterr().err


def test_session_direct_call_parse_clargs():
    """directly call the parse_clargs() function otherwise not covered"""
    if len(sys.argv) > 1:
        with pytest.raises(SystemExit, match='2'):
            run_session.parse_clargs()
    else:
        run_session.parse_clargs()


def test_texts_script_instant(model_file):
    """test texts script cli tool in instant evaluation mode"""
    command = ['texts', 'script', '-f', model_file]
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == "program output: >>>\n1\n<<<\n"


def test_texts_script_deferred(model_file):
    """test texts script cli tool in deferred evaluation mode"""
    command = ['texts', 'script', '-f', model_file, '-m', 'deferred']
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == "program output: >>>\n1\n<<<\n"


def test_texts_script_workflow(model_file, lpad_file):
    """test texts script cli tool in workflow evaluation mode"""
    command = ['texts', 'script', '-f', model_file, '-m', 'workflow',
               '-l', lpad_file, '-r']
    with sp.Popen(command, stdout=sp.PIPE, shell=False) as proc:
        assert "program output: >>>\n1\n<<<\n" in proc.stdout.read().decode()


def test_texts_script_show_model(model_file):
    """test texts script cli tool with the --show-model option"""
    command = ['texts', 'script', '-f', model_file, '--show-model']
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert proc.stderr.read().decode() == ''


def test_texts_script_no_interpreter(model_file):
    """test texts script cli tool with the --no-interpreter option"""
    command = ['texts', 'script', '-f', model_file, '--no-interpreter']
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        assert proc.stdout.read().decode() == ''
        assert proc.stderr.read().decode() == ''


def test_texts_session(lpad_file, _res_config_loc):
    """test texts session cli tool"""
    model = "a = 1; print(a)\n%exit"
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0]
        assert "Output > 1" in stdout.decode()


def test_texts_session_expression(lpad_file, _res_config_loc):
    """test texts session cli tool with expression"""
    model = "a = 1 \n a + 1 \n %exit"
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0]
        assert "Output > 2" in stdout.decode()


def test_texts_session_magics(lpad_file, _res_config_loc):
    """test texts session cli tool with magics"""
    model = "%uuid \n %sleep \n %new \n %start \n %stop \n %hist \n %vary \n %exit"
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        _, stderr = proc.communicate(input=model.encode())
    assert stderr.decode() == ''


def test_texts_session_rerun(lpad_file, _res_config_loc):
    """test texts session rerun magic"""
    model = "a = 1; print(a)\n%rerun a\n%rerun b\n%exit"
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Variable update error: Variable b not found in the model.' in stderr


def test_texts_session_switch_model(lpad, lpad_file, _res_config_loc):
    """test texts session switch model uuid"""
    model_uuid = Session(lpad, grammar_path=GRAMMAR_LOC, create_new=True).uuid
    command = ['texts', 'session', '-l', lpad_file]
    model = f'%uuid {model_uuid}\n%uuid\n%exit'
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert model_uuid in stdout
    fake_uuid = '45f5f9a390b94359974661b55f5585af'
    model = f'%uuid {fake_uuid}\n%exit'
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert f'Model not found: uuid {fake_uuid}' in stderr


def test_texts_session_tag_and_search_model(lpad_file, _res_config_loc):
    """test model tagging and searching in tags section"""
    model = "tag ((doping: 'Fe'), ('active site': 'M5'), (n: (5, 7)))\n%tag"
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert "((doping: 'Fe'), ('active site': 'M5'), (n: (5, 7)))" in stdout
    model = "%find ((tags: (('~doping': (('$in': ('Fe', 'Co'))) )) ))"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout, _ = proc.communicate(input=model.encode())
    assert 'READY' in stdout.decode()
    model = "%find {tags: {'~active site': {'$in': ('M1', 'M5')}}}"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout, _ = proc.communicate(input=model.encode())
    assert 'READY' in stdout.decode()


def test_texts_session_tag_and_search_model_errors(lpad_file, _res_config_loc):
    """test model tagging and searching with errors"""
    model = "tag ((doping: 'Fe', 'Co'), ('active site': 'M5'))"
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Tag err' in stderr
    assert 'tag table must have only one row' in stderr
    model = "%find (('~doping': (('$in': ('Fe', 'Co'))) ))"
    with sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE, shell=False) as proc:
        stderr = proc.communicate(input=model.encode())[1].decode()
    assert 'Query error: query must include tags, meta or data keys' in stderr


def test_texts_session_search_model_data(lpad_file, _res_config_loc):
    """test model searching in data section"""
    var_a = 'a_' + uuid.uuid4().hex
    model = f"{var_a} = '{var_a}'; b = {var_a}; print(b)\n"
    model += "%find {data: {'~"
    model += var_a
    model += "': {'$exists': true}}}\n%exit"
    command = ['texts', 'session', '-l', lpad_file, '-r']
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert var_a in stdout
    assert 'COMPLETED ' in stdout


def test_texts_session_search_tags_load_one(lpad_file, _res_config_loc):
    """test searching models in tags section and load one"""
    model = "tag ((doping: 'Fe'), ('active site': 'M5'))"
    command = ['texts', 'session', '-l', lpad_file]
    with sp.Popen(command, stdin=sp.PIPE, shell=False) as proc:
        proc.communicate(input=model.encode())
    model = "%find {tags: {'~doping': {'$in': ('Fe', 'Co')}}} load one"
    with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, shell=False) as proc:
        stdout = proc.communicate(input=model.encode())[0].decode()
    assert "uuids: '" in stdout
