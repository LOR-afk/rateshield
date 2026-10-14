CREATE TABLE policies (
  id INT PRIMARY KEY,
  max_requests INT NOT NULL,
  window_seconds INT NOT NULL,
  failed_login_threshold INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE security_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  client_ip VARCHAR(45) NOT NULL,
  kind VARCHAR(32) NOT NULL,
  endpoint VARCHAR(128) NOT NULL,
  status_code INT NOT NULL,
  detail VARCHAR(120) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_events_ip_time (client_ip, created_at)
);
