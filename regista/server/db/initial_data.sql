INSERT INTO job (jid, job_name, job_type, author, cron, max_run_count)
VALUES 
(1, 'regista_id', 0, 'user1', NULL, 2),
(2, 'calendar', 0, 'user1', '0 12 1-5 * *', 2),
(3, 'dm1', 0, 'user1', NULL, 2),
(4, 'dm2', 0, 'user1', NULL, 2),
(5, 'dm3', 0, 'user1', NULL, 2),
(6, 'dm4', 0, 'user1', NULL, 2)

INSERT INTO job_dependency (jid, dependent_jid)
VALUES 
(3, 1),
(3, 2),
(4, 3),
(6, 4),
(6, 5)
