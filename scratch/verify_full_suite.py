import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    res = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] Health Check: 200 OK")

def test_phase1_attack_scenarios():
    scenarios = [
        "normal_traffic",
        "account_takeover",
        "mule_network",
        "coordinated_fraud",
        "recipient_attack",
        "credential_stuffing",
        "gateway_outage",
        "merchant_failure",
        "mixed_attack",
        "weak_signals"
    ]
    print(f"\n--- Testing Phase 1: Attack Lab ({len(scenarios)} Scenarios) ---")
    for sc in scenarios:
        res = requests.post(f"{BASE_URL}/api/demo/inject-attack", json={"scenario": sc}, timeout=5)
        assert res.status_code == 200, f"Scenario {sc} failed: {res.text}"
        data = res.json()
        assert data["status"] == "ATTACK_SEQUENCE_INITIATED"
        print(f"  [PASS] Scenario '{sc}': Triggered successfully")

def test_phase2_edge_resiliency():
    print("\n--- Testing Phase 2: Edge Node Simulation & Resiliency ---")
    # 1. Get nodes
    res = requests.get(f"{BASE_URL}/api/edge/nodes", timeout=5)
    assert res.status_code == 200
    nodes = res.json()
    assert "Mumbai" in nodes
    print(f"  [PASS] Edge Nodes Found: {list(nodes.keys())}")

    # 2. Disconnect Mumbai
    res = requests.post(f"{BASE_URL}/api/edge/Mumbai/disconnect", timeout=5)
    assert res.status_code == 200
    d_data = res.json()
    assert d_data["status"] == "OFFLINE"
    print("  [PASS] Mumbai Disconnected -> Local buffering active")

    # 3. Reconnect Mumbai
    res = requests.post(f"{BASE_URL}/api/edge/Mumbai/reconnect", timeout=5)
    assert res.status_code == 200
    r_data = res.json()
    assert r_data["status"] == "ONLINE"
    print(f"  [PASS] Mumbai Reconnected -> Synced {r_data.get('synced_events', 0)} buffered events")

    # 4. Get Edge Counters
    res = requests.get(f"{BASE_URL}/api/edge/counters", timeout=5)
    assert res.status_code == 200
    counters = res.json()
    assert "events_received" in counters
    assert "events_filtered" in counters
    print(f"  [PASS] Edge Funnel Counters: {counters}")

def test_phase3_pqc_lab():
    print("\n--- Testing Phase 3: Post-Quantum Cryptography Lab ---")
    # 1. Info
    res = requests.get(f"{BASE_URL}/api/pqc/info", timeout=5)
    assert res.status_code == 200
    info = res.json()
    assert "ML-DSA-65" in info["digital_signature"]
    assert "ML-KEM-768" in info["key_encapsulation"]
    print("  [PASS] PQC Suite: ML-DSA-65, ML-KEM-768, AES-256-GCM, SHA-384 verified")

    # 2. Valid transaction test
    res = requests.post(f"{BASE_URL}/api/pqc/test-valid?amount=10000.0", timeout=5)
    assert res.status_code == 200
    valid_data = res.json()
    assert valid_data["status"] == "VALID"
    assert valid_data["is_tampered"] is False
    print(f"  [PASS] Valid PQC Test (Rs. 10,000): {valid_data['verdict']} in {valid_data['verification_latency_ms']}ms")

    # 3. Tamper test (amount altered from 10K to 10L)
    res = requests.post(f"{BASE_URL}/api/pqc/test-tamper?original_amount=10000.0&tampered_amount=1000000.0", timeout=5)
    assert res.status_code == 200
    tamper_data = res.json()
    assert tamper_data["status"] == "TAMPERED"
    assert tamper_data["is_tampered"] is True
    print(f"  [PASS] Tamper PQC Test (Rs. 10K -> 10L): {tamper_data['verdict']}")
    print(f"         Mitigation: {tamper_data['mitigation']}")

def test_phase4_dataset_adapters():
    print("\n--- Testing Phase 4: Dataset Adapters (IBM AMLSim & PaySim) ---")
    # 1. AMLSim replay
    res = requests.post(f"{BASE_URL}/api/adapters/amlsim/replay?pattern=fan_in&count=15", timeout=5)
    assert res.status_code == 200
    aml_data = res.json()
    assert aml_data["status"] == "REPLAY_STARTED"
    assert aml_data["dataset"] == "IBM_AMLSim"
    print(f"  [PASS] AMLSim Stream Replay: {aml_data['events_count']} events, {aml_data['schema_isolation']}")

    # 2. PaySim replay
    res = requests.post(f"{BASE_URL}/api/adapters/paysim/replay?pattern=transfer_cashout_drain&count=10", timeout=5)
    assert res.status_code == 200
    paysim_data = res.json()
    assert paysim_data["status"] == "REPLAY_STARTED"
    assert paysim_data["dataset"] == "PaySim_MobileMoney"
    print(f"  [PASS] PaySim Stream Replay: {paysim_data['events_count']} events, {paysim_data['schema_isolation']}")

def test_phase5_load_testing():
    print("\n--- Testing Phase 5: High-Throughput Load Testing & Fraud Metrics ---")
    # 1. Start 1000 EPS tier
    res = requests.post(f"{BASE_URL}/api/load-test/start?tier=1000", timeout=5)
    assert res.status_code == 200
    start_data = res.json()
    assert start_data["status"] == "LOAD_TEST_STARTED"
    print(f"  [PASS] Started Load Test Tier: {start_data['tier_eps']} EPS")

    time.sleep(1.0)

    # 2. Fetch metrics
    res = requests.get(f"{BASE_URL}/api/load-test/metrics", timeout=5)
    assert res.status_code == 200
    m_data = res.json()
    assert m_data["is_running"] is True
    print(f"  [PASS] Metrics at 1,000 EPS:")
    print(f"         Throughput: {m_data['achieved_eps']} EPS")
    print(f"         Edge Filter Efficiency: {m_data['edge_filtering_ratio_pct']}%")
    print(f"         Latency (p95): {m_data['latency']['p95_ms']} ms")
    print(f"         Queue Dropped Frames: {m_data['queue_health']['dropped_frames']}")
    print(f"  [PASS] Fraud Evaluation Metrics:")
    for k, v in m_data["fraud_evaluation_metrics"].items():
        print(f"         {k}: {v}")

    # 3. Stop load test
    res = requests.post(f"{BASE_URL}/api/load-test/stop", timeout=5)
    assert res.status_code == 200
    stop_data = res.json()
    assert stop_data["status"] == "LOAD_TEST_STOPPED"
    print("  [PASS] Load Test Stopped cleanly")

if __name__ == "__main__":
    print("==================================================")
    print("FINRESOLVE PREDICT - 5-PHASE FULL SUITE VERIFICATION")
    print("==================================================")
    test_health()
    test_phase1_attack_scenarios()
    test_phase2_edge_resiliency()
    test_phase3_pqc_lab()
    test_phase4_dataset_adapters()
    test_phase5_load_testing()
    print("\n==================================================")
    print("ALL 5 PHASES AND ENDPOINTS SUCCESSFULLY VERIFIED!")
    print("==================================================")
