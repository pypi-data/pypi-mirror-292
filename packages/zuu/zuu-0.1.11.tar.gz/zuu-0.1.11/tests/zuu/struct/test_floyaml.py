import time
import pprint
from src.zuu.struct.floyaml import FloYaml

data1 = """
val1: 1
val2: 2
    val3: 3
    val3: 4
        val5: 5
    val3 : 6
        val5: 10
        val5: 11
    val5: 7
"""

data2 = """\
task: operation-alpha
  time_start: 13:00
  time_limit: 60min
  action: initiate-alpha
    execute: ${path_generic}/exec_cmd alpha --target ${target_alpha}

  on_completion: cleanup-alpha
    terminate_all: True

task: operation-beta
  time_start: 14:00
  time_limit: 60min
  action: initiate-beta
    execute: ${path_generic}/exec_cmd beta {param_beta}
    wait: 1min

  on_completion: cleanup-beta
    terminate_all: True

task: operation-gamma
  time_start: 15:00
  time_limit: 60min
  action: initiate-gamma
    execute: ${path_generic}/exec_cmd gamma {param_gamma}
     
  on_completion: cleanup-gamma
    terminate_all: True

process: procedure-delta
  boundary: all
  frequency: 5min

procedure: process-epsilon
  trigger: ${path_generic}/exec_cmd epsilon
    run: ${path_generic}/exec_cmd kill --name ${name_epsilon}

procedure: process-zeta
  trigger: ${path_generic}/exec_cmd zeta-launch
    run: ${path_generic}/exec_cmd launch --name ${name_zeta} --package ${pkg_zeta}
"""


def test_load_and_instance():
    starttime = time.time()
    parsed = FloYaml.load(data1)
    print(time.time() - starttime)
    assert isinstance(parsed, FloYaml)


def test_retrieve_all_val3():
    parsed = FloYaml.load(data1)
    assert parsed["val2", FloYaml.VAL("val3")] == [3, 4, 6]


def test_retrieve_first_val3():
    parsed = FloYaml.load(data1)
    assert parsed["val2", FloYaml.VAL("val3[0]")] == 3


def test_update_first_val3():
    parsed = FloYaml.load(data1)
    parsed["val2", FloYaml.VAL("val3[0]")] = 4
    assert parsed["val2", FloYaml.VAL("val3[0]")] == 4


def test_retrieve_all_val3_after_update():
    parsed = FloYaml.load(data1)
    parsed["val2", FloYaml.VAL("val3[0]")] = 4
    assert parsed["val2", FloYaml.VAL("val3")] == [4, 4, 6]


def test_retrieve_all_val5_under_third_val3():
    parsed = FloYaml.load(data1)
    assert parsed["val2", "val3[2]", FloYaml.VAL("val5")] == [10, 11]


def test_retrieve_second_val5_under_third_val3():
    parsed = FloYaml.load(data1)
    assert parsed["val2", "val3[2]", "val5[1]"] == 11


def test_retrieve_dict_under_second_val3():
    parsed = FloYaml.load(data1)
    assert parsed["val2", "val3[1]"] == {"__val__": 4, "val5": 5}


def test_dumps():
    parsed = FloYaml.load(data1)
    dumped = parsed.dumps()
    dumped = dumped.splitlines()
    # Add assertions here if you want to check the content of dumped


def test_process_data2():
    processed = FloYaml(data2)
    pprint.pprint(processed.datadict)
    # Add assertions here if you want to check the content of processed.datadict
