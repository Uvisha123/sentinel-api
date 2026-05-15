import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

# Random seed for reproducibility: same seed = same dataset every time you run
RANDOM_SEED = 42

# How many normal IPs vs attack IPs to simulate
NUM_NORMAL_IPS = 180       # 180 clearly normal users
NUM_NOISY_NORMAL_IPS = 20  # 20 "noisy" normal users (power users, devs, health checks)
NUM_BRUTEFORCE_IPS = 15    # 15 brute-force attackers
NUM_SCRAPER_IPS = 15       # 15 scraper bots
NUM_CREDENTIAL_IPS = 15    # 15 credential stuffing attackers

# Time window: we simulate 1 hour of traffic
SIMULATION_DURATION_MINUTES = 60

# Realistic endpoints that SentinelAPI would serve
NORMAL_ENDPOINTS = [
    "/auth/login",
    "/auth/register",
    "/api/keys",
    "/api/keys/generate",
    "/analytics/requests",
    "/analytics/summary",
    "/security/blocked-ips",
    "/security/rate-limits",
    "/users/profile",
    "/users/settings",
    "/docs",
    "/health",
]

# User agents — normal users have 1-2, attackers may use many (or just one)
NORMAL_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14) Chrome/120.0.0.0 Mobile",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0",
]

BOT_USER_AGENTS = [
    "python-requests/2.31.0",
    "Go-http-client/1.1",
    "curl/7.88.1",
    "Scrapy/2.11.0",
    "axios/1.6.2",
    "Java/17.0.1",
    "PostmanRuntime/7.36.0",
    "custom-bot/1.0",
]

# Output path
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "synthetic_requests.csv")



def generate_ip(prefix: str, index: int) -> str:
    third_octet = (index // 254) + 1   # rolls over after 254
    fourth_octet = (index % 254) + 1   # stays in 1-254 range
    return f"{prefix}.{third_octet}.{fourth_octet}"


def random_timestamps(rng: np.random.Generator, start: datetime,duration_minutes: int, count: int,bursty: bool = False) -> list:
    total_seconds = duration_minutes * 60
    
    if bursty:
        num_bursts = rng.integers(2, 5)
        burst_centers = rng.integers(0, total_seconds, size=num_bursts)
        burst_spread = 30  # seconds — how wide each burst is
        
        offsets = []
        for _ in range(count):
            # Pick a random burst center, then add noise around it
            center = rng.choice(burst_centers)
            offset = center + rng.normal(0, burst_spread)
            offset = np.clip(offset, 0, total_seconds)  # keep in bounds
            offsets.append(offset)
    else:
        # Normal traffic: uniformly distributed across the whole window
        offsets = rng.uniform(0, total_seconds, size=count)
    
    timestamps = [start + timedelta(seconds=float(s)) for s in sorted(offsets)]
    return timestamps


# TRAFFIC GENERATORS — One function per traffic type
def generate_normal_traffic(rng: np.random.Generator, start_time: datetime) -> pd.DataFrame:
    
    rows = []
    
    for i in range(NUM_NORMAL_IPS):
        ip = generate_ip("10.0", i)
        
        # Each normal user makes 5-30 requests per hour
        num_requests = rng.integers(5, 31)
        
        # They use 1-2 user agents (same device, maybe desktop + mobile)
        user_agents = rng.choice(NORMAL_USER_AGENTS,size=rng.integers(1, 3),replace=False).tolist()
        
        timestamps = random_timestamps(rng, start_time,SIMULATION_DURATION_MINUTES,num_requests, bursty=False)
        
        for ts in timestamps:
            endpoint = rng.choice(NORMAL_ENDPOINTS)
            
            # Status codes: 85% 200, 5% 201, 5% 400, 3% 404, 2% 500
            status = rng.choice([200, 201, 400, 404, 500], p=[0.85, 0.05, 0.05, 0.03, 0.02])
            
            # Response time: normal distribution around 150ms
            response_time = max(20, int(rng.normal(150, 60)))
            
            rows.append({
                "ip": ip,
                "timestamp": ts.isoformat(),
                "endpoint": endpoint,
                "status_code": status,
                "response_time_ms": response_time,
                "user_agent": rng.choice(user_agents),
                "is_attack": 0,
                "attack_type": "normal",
            })
    
    return pd.DataFrame(rows)


def generate_noisy_normal_traffic(rng: np.random.Generator, start_time: datetime) -> pd.DataFrame:
    
    rows = []

    for i in range(NUM_NOISY_NORMAL_IPS):
        ip = generate_ip("10.1", i)

        # Noisy normals make MORE requests than typical users (25-60)
        num_requests = rng.integers(25, 61)

        # Some use multiple user agents (testing from different devices)
        user_agents = rng.choice(NORMAL_USER_AGENTS + BOT_USER_AGENTS[:2],size=rng.integers(1, 4),replace=False).tolist()

        timestamps = random_timestamps(rng, start_time,SIMULATION_DURATION_MINUTES,num_requests, bursty=False)

        for ts in timestamps:
            endpoint = rng.choice(NORMAL_ENDPOINTS)

            # Higher error rate than normal (15-25% errors) but not attack-level
            status = rng.choice([200, 201, 400, 401, 404, 500],p=[0.65, 0.10, 0.08, 0.07, 0.05, 0.05])

            response_time = max(20, int(rng.normal(120, 50)))

            rows.append({
                "ip": ip,
                "timestamp": ts.isoformat(),
                "endpoint": endpoint,
                "status_code": status,
                "response_time_ms": response_time,
                "user_agent": rng.choice(user_agents),
                "is_attack": 0,
                "attack_type": "normal",
            })

    return pd.DataFrame(rows)


def generate_bruteforce_traffic(rng: np.random.Generator, start_time: datetime) -> pd.DataFrame:
    
    rows = []
    
    # The target endpoint for brute-force is almost always login
    target_endpoint = "/auth/login"
    
    for i in range(NUM_BRUTEFORCE_IPS):
        ip = generate_ip("192.168", i)
        
        # High request volume: 50-150 requests in one hour
        num_requests = rng.integers(50, 151)
        
        # Attackers typically use a single automated user agent
        user_agent = rng.choice(BOT_USER_AGENTS)
        
        # Bursty=True because brute-force often comes in waves
        timestamps = random_timestamps(rng, start_time,SIMULATION_DURATION_MINUTES,num_requests, bursty=True)
        
        for ts in timestamps:
            # 90% of requests hit the target, 10% might probe other endpoints
            if rng.random() < 0.90:
                endpoint = target_endpoint
            else:
                endpoint = rng.choice(["/auth/register", "/users/profile"])
            
            # 80% 401 (wrong password), 10% 200 (lucky guess), 10% 429 (rate limited)
            status = rng.choice([401, 200, 429],p=[0.80, 0.10, 0.10])
            
            # Fast, consistent response times (automated tool, no human delay)
            response_time = max(10, int(rng.normal(40, 10)))
            
            rows.append({
                "ip": ip,
                "timestamp": ts.isoformat(),
                "endpoint": endpoint,
                "status_code": status,
                "response_time_ms": response_time,
                "user_agent": user_agent,
                "is_attack": 1,
                "attack_type": "bruteforce",
            })
    
    return pd.DataFrame(rows)


def generate_scraper_traffic(rng: np.random.Generator, start_time: datetime) -> pd.DataFrame:
    
    rows = []
    
    # Scrapers try many endpoints — we add more to simulate probing
    scraper_endpoints = NORMAL_ENDPOINTS + [
        "/api/v1/data",
        "/api/v2/data",
        "/admin/config",
        "/admin/users",
        "/internal/status",
        "/debug/vars",
        "/api/export",
        "/api/keys/list",
    ]
    
    for i in range(NUM_SCRAPER_IPS):
        ip = generate_ip("172.16", i)
        
        num_requests = rng.integers(40, 101)
        
        num_agents = rng.integers(2, 5)
        user_agents = rng.choice(BOT_USER_AGENTS, size=num_agents,replace=False).tolist()
        
        timestamps = random_timestamps(rng, start_time,SIMULATION_DURATION_MINUTES,num_requests, bursty=False)
        
        for j, ts in enumerate(timestamps):
            # Systematically cycle through endpoints (not random — sequential)
            endpoint = scraper_endpoints[j % len(scraper_endpoints)]
            
            # Mostly successful: 75% 200, 10% 403, 10% 404, 5% 500
            status = rng.choice([200, 403, 404, 500],p=[0.75, 0.10, 0.10, 0.05])
            
            # Fairly consistent response times (automated)
            response_time = max(15, int(rng.normal(60, 15)))
            
            rows.append({
                "ip": ip,
                "timestamp": ts.isoformat(),
                "endpoint": endpoint,
                "status_code": status,
                "response_time_ms": response_time,
                "user_agent": rng.choice(user_agents),
                "is_attack": 1,
                "attack_type": "scraper",
            })
    
    return pd.DataFrame(rows)


def generate_credential_stuffing_traffic(rng: np.random.Generator,start_time: datetime) -> pd.DataFrame:

    rows = []
    
    # Only targets auth-related endpoints
    target_endpoints = ["/auth/login", "/auth/register", "/users/profile"]
    
    for i in range(NUM_CREDENTIAL_IPS):
        ip = generate_ip("203.0", i)
        
        # High volume, concentrated in bursts
        num_requests = rng.integers(60, 121)
        
        # Rotate through many user agents to evade detection
        num_agents = rng.integers(3, 7)
        user_agents = rng.choice(NORMAL_USER_AGENTS + BOT_USER_AGENTS,size=min(num_agents, len(NORMAL_USER_AGENTS) + len(BOT_USER_AGENTS)),replace=False).tolist()
        
        # BURSTY = True — this is the key characteristic
        timestamps = random_timestamps(rng, start_time,SIMULATION_DURATION_MINUTES,num_requests, bursty=True)
        
        for ts in timestamps:
            endpoint = rng.choice(target_endpoints, p=[0.70, 0.20, 0.10])
            
            # 75% 401, 5% 200, 15% 429, 5% 403
            status = rng.choice([401, 200, 429, 403],p=[0.75, 0.05, 0.15, 0.05])
            
            # Fast response (automated), slight variation from agent rotation
            response_time = max(10, int(rng.normal(50, 20)))
            
            rows.append({
                "ip": ip,
                "timestamp": ts.isoformat(),
                "endpoint": endpoint,
                "status_code": status,
                "response_time_ms": response_time,
                "user_agent": rng.choice(user_agents),
                "is_attack": 1,
                "attack_type": "credential_stuffing",
            })
    
    return pd.DataFrame(rows)


# MAIN PIPELINE — Combine all traffic and save
def generate_dataset() -> pd.DataFrame:

    rng = np.random.default_rng(RANDOM_SEED)
    
    # Simulation start time
    start_time = datetime(2025, 5, 12, 10, 0, 0)  # May 12, 2025, 10:00 AM
    
    print("=" * 60)
    print("🛡️  SentinelAPI — Synthetic Data Generator")
    print("=" * 60)
    
    # Step 2: Generate each traffic type
    print("\n📊 Generating normal traffic...")
    normal_df = generate_normal_traffic(rng, start_time)
    print(f"   ✅ {len(normal_df)} normal requests from {NUM_NORMAL_IPS} IPs")
    
    print("\n📊 Generating noisy normal traffic...")
    noisy_df = generate_noisy_normal_traffic(rng, start_time)
    print(f"   ✅ {len(noisy_df)} noisy normal requests from {NUM_NOISY_NORMAL_IPS} IPs")
    
    print("\n🔴 Generating brute-force attacks...")
    brute_df = generate_bruteforce_traffic(rng, start_time)
    print(f"   ✅ {len(brute_df)} brute-force requests from {NUM_BRUTEFORCE_IPS} IPs")
    
    print("\n🟡 Generating scraper traffic...")
    scraper_df = generate_scraper_traffic(rng, start_time)
    print(f"   ✅ {len(scraper_df)} scraper requests from {NUM_SCRAPER_IPS} IPs")
    
    print("\n🟠 Generating credential stuffing...")
    cred_df = generate_credential_stuffing_traffic(rng, start_time)
    print(f"   ✅ {len(cred_df)} credential stuffing requests from {NUM_CREDENTIAL_IPS} IPs")
    
    # Step 3: Combine all DataFrames
    full_df = pd.concat([normal_df, noisy_df, brute_df, scraper_df, cred_df],ignore_index=True)
    
    # Step 4: Sort by timestamp (chronological order)
    full_df["timestamp"] = pd.to_datetime(full_df["timestamp"], format="ISO8601")
    full_df = full_df.sort_values("timestamp").reset_index(drop=True)
    
    # Step 5: Save to CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    full_df.to_csv(OUTPUT_FILE, index=False)
    
    # Step 6: Print summary statistics
    print("\n" + "=" * 60)
    print("📈 DATASET SUMMARY")
    print("=" * 60)
    print(f"\n   Total rows:           {len(full_df)}")
    print(f"   Unique IPs:           {full_df['ip'].nunique()}")
    print(f"   Time range:           {full_df['timestamp'].min()} → {full_df['timestamp'].max()}")
    print(f"\n   Normal requests:      {len(full_df[full_df['is_attack'] == 0])} "
          f"({len(full_df[full_df['is_attack'] == 0]) / len(full_df) * 100:.1f}%)")
    print(f"   Attack requests:      {len(full_df[full_df['is_attack'] == 1])} "
          f"({len(full_df[full_df['is_attack'] == 1]) / len(full_df) * 100:.1f}%)")
    
    print("\n   Attack breakdown:")
    for attack_type in ["bruteforce", "scraper", "credential_stuffing"]:
        count = len(full_df[full_df["attack_type"] == attack_type])
        print(f"   - {attack_type:25s}: {count:5d} requests")
    
    print(f"\n   Status code distribution:")
    for code, count in full_df["status_code"].value_counts().sort_index().items():
        print(f"   - {code}: {count:5d} ({count / len(full_df) * 100:.1f}%)")
    
    print(f"\n   💾 Saved to: {OUTPUT_FILE}")
    print("=" * 60)
    
    return full_df


# ENTRY POINT

if __name__ == "__main__":
    df = generate_dataset()
    
    # Quick sanity check: show a few rows from each category
    print("\n\n📋 SAMPLE ROWS (3 per category):")
    print("-" * 100)
    for attack_type in ["normal", "bruteforce", "scraper", "credential_stuffing"]:
        print(f"\n--- {attack_type.upper()} ---")
        sample = df[df["attack_type"] == attack_type].head(3)
        print(sample[["ip", "timestamp", "endpoint", "status_code","response_time_ms", "user_agent"]].to_string(index=False))
