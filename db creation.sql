CREATE TABLE company(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
name VARCHAR(255) NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
website VARCHAR (500),
created_at TIMESTAMP DEFAULT NOW(),
is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE users(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
company_id UUID REFERENCES company(id) ON DELETE SET NULL,
email VARCHAR(255) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
full_name VARCHAR(255) NOT NULL,
loom_video_url VARCHAR(500),
upwork_agency_id VARCHAR(255),
tone_preference VARCHAR(50) DEFAULT 'casual',
created_at TIMESTAMP DEFAULT NOW(),
is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE profile(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
company_id UUID REFERENCES company(id) ON DELETE CASCADE,
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
headline VARCHAR(255),
bio TEXT,
skills TEXT[],
hourly_rate DECIMAL(10,2),
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE profile_platforms(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
profile_id UUID REFERENCES profile(id) ON DELETE CASCADE,
platform_name VARCHAR(50) NOT NULL,
platform_user_id VARCHAR(255),
access_token TEXT,
connected_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE profile_owners(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
profile_id UUID REFERENCES profile(id) ON DELETE CASCADE,
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
ownership_type VARCHAR(50),
joined_at TIMESTAMP DEFAULT NOW(),
is_primary BOOLEAN DEFAULT FALSE
);

CREATE TABLE banks(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
owner_id UUID REFERENCES profile_owners(id) ON DELETE CASCADE,
bank_name VARCHAR(255) NOT NULL,
account_number VARCHAR(255),
routing_number VARCHAR(255),
currency VARCHAR(10) DEFAULT 'USD',
is_primary BOOLEAN DEFAULT FALSE
);

CREATE TABLE nominees(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
owner_id UUID REFERENCES profile_owners(id) ON DELETE CASCADE,
full_name VARCHAR(255) NOT NULL,
email VARCHAR(255),
phone VARCHAR(50),
relationship VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscription_plans(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
name VARCHAR(255) NOT NULL,
price_per_month DECIMAL(10,2),
price_per_response DECIMAL(10,2),
features JSONB,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_subscriptions(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
plan_id UUID REFERENCES subscription_plans(id) ON DELETE SET NULL,
started_at TIMESTAMP DEFAULT NOW(),
ends_at TIMESTAMP,
status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE job_feeds(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
platform_id UUID REFERENCES profile_platforms(id) ON DELETE SET NULL,
keywords TEXT[],
min_hourly_rate DECIMAL(10,2),
min_fixed_rate DECIMAL(10,2),
skip_if_contains TEXT[],
blocked_clients TEXT[],
min_client_rating DECIMAL(5,2),
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE jobs(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
upwork_job_id VARCHAR(255) UNIQUE,
title VARCHAR(500) NOT NULL,
description TEXT,
budget_type VARCHAR(50),
budget_min DECIMAL(10,2),
budget_max DECIMAL(10,2),
client_rating DECIMAL(5,2),
category VARCHAR(255),
posted_at TIMESTAMP,
fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE job_matches(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
feed_id UUID REFERENCES job_feeds(id) ON DELETE CASCADE,
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
match_score DECIMAL(5,2),
status VARCHAR(50) DEFAULT 'pending',
matched_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE proposals(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
match_id UUID REFERENCES job_matches(id) ON DELETE CASCADE,
content TEXT,
loom_url VARCHAR(500),
bid_rate DECIMAL(10,2),
ai_model_used VARCHAR(100),
status VARCHAR(50) DEFAULT 'draft',
sent_at TIMESTAMP,
opened_at TIMESTAMP,
responded_at TIMESTAMP,
closed_at TIMESTAMP
);

CREATE TABLE ai_generation_logs(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
proposal_id UUID REFERENCES proposals(id) ON DELETE CASCADE,
model VARCHAR(100),
prompt_tokens INT,
completion_tokens INT,
cost DECIMAL(10,6),
error_message TEXT,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE business_managers(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
name VARCHAR(255) NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
proposals_sent_today INT DEFAULT 0,
is_available BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE proposal_assignments(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
proposal_id UUID REFERENCES proposals(id) ON DELETE CASCADE,
manager_id UUID REFERENCES business_managers(id) ON DELETE SET NULL,
assigned_at TIMESTAMP DEFAULT NOW(),
sent_at TIMESTAMP
);

CREATE TABLE connects_tracking(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
balance INT DEFAULT 0,
used INT DEFAULT 0,
updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notifications(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
type VARCHAR(100),
message TEXT,
is_read BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE referrals(
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
referrer_id UUID REFERENCES users(id) ON DELETE SET NULL,
referred_id UUID REFERENCES users(id) ON DELETE SET NULL,
commission_rate DECIMAL(5,2) DEFAULT 50.00,
total_earned DECIMAL(10,2) DEFAULT 0,
created_at TIMESTAMP DEFAULT NOW()
);