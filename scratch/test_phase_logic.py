import sys
import os
sys.path.insert(0, r"c:\Hack2Ignite\finresolve\backend")

from pqc_lab import pqc_lab
from adapters import amlsim_adapter, paysim_adapter
from load_test_engine import load_test_engine
from anomaly_engine import anomaly_engine

def test_pqc():
    valid_res = pqc_lab.run_valid_test(10000.0)
    assert valid_res["status"] == "VALID"
    assert valid_res["sha384_expected"] == valid_res["sha384_computed"]
    print("[PASS] PQC Valid Test PASSED:", valid_res["verdict"])

    tamper_res = pqc_lab.run_tamper_test(10000.0, 1000000.0)
    assert tamper_res["status"] == "TAMPERED"
    assert tamper_res["sha384_expected"] != tamper_res["sha384_computed"]
    print("[PASS] PQC Tamper Test PASSED:", tamper_res["verdict"])

def test_edge():
    # Disconnect Mumbai
    d_res = anomaly_engine.disconnect_edge_node("Mumbai")
    assert d_res["status"] == "OFFLINE"
    assert anomaly_engine.edge_node_stats["Mumbai"]["status"] == "OFFLINE"
    print("[PASS] Edge Disconnect PASSED:", d_res)

    # Reconnect Mumbai
    r_res = anomaly_engine.reconnect_and_sync_edge_node("Mumbai")
    assert r_res["status"] == "ONLINE"
    assert anomaly_engine.edge_node_stats["Mumbai"]["status"] == "ONLINE"
    print("[PASS] Edge Reconnect PASSED:", r_res)

def test_adapters():
    aml_events = amlsim_adapter.generate_synthetic_stream("fan_in", 10)
    assert len(aml_events) == 10
    assert aml_events[0].metadata["source_dataset"] == "IBM_AMLSim"
    print("[PASS] AMLSim Adapter PASSED: 10 events generated strictly isolated")

    paysim_events = paysim_adapter.generate_synthetic_stream("transfer_cashout_drain", 10)
    assert len(paysim_events) == 10
    assert paysim_events[0].metadata["source_dataset"] == "PaySim_MobileMoney"
    print("[PASS] PaySim Adapter PASSED: 10 events generated strictly isolated")

def test_load():
    load_test_engine.start(100)
    st = load_test_engine.get_status()
    assert st["is_running"] is True
    assert "fraud_evaluation_metrics" in st
    load_test_engine.stop()
    print("[PASS] Load Test Engine PASSED:", st["fraud_evaluation_metrics"]["benchmark_note"])

if __name__ == "__main__":
    test_pqc()
    test_edge()
    test_adapters()
    test_load()
    print("\nALL PHASE 1-5 BACKEND LOGIC VERIFIED!")
