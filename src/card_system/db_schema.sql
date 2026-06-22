CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO users (id, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'default');

CREATE TABLE IF NOT EXISTS documents (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    file_path VARCHAR(1024),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS document_chunks (
    id CHAR(36) PRIMARY KEY,
    document_id CHAR(36) NOT NULL,
    chunk_index INT NOT NULL,
    content LONGTEXT NOT NULL,
    metadata JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_document_chunks_document_index (document_id, chunk_index),
    CONSTRAINT fk_document_chunks_document
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS knowledge_cards (
    id CHAR(36) PRIMARY KEY,
    document_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    keywords JSON NOT NULL,
    explanation LONGTEXT NOT NULL,
    example TEXT NOT NULL,
    common_mistakes JSON NOT NULL,
    related_concepts JSON NOT NULL,
    source_text LONGTEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_knowledge_cards_document
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS quiz_questions (
    id CHAR(36) PRIMARY KEY,
    card_id CHAR(36) NOT NULL,
    question_type VARCHAR(64) NOT NULL,
    question LONGTEXT NOT NULL,
    options JSON NOT NULL,
    answer TEXT NOT NULL,
    explanation LONGTEXT NOT NULL,
    difficulty VARCHAR(32) NOT NULL DEFAULT 'medium',
    related_card_title VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_quiz_questions_card
        FOREIGN KEY (card_id) REFERENCES knowledge_cards(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS answer_records (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    question_id CHAR(36) NOT NULL,
    user_answer LONGTEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    score DOUBLE NOT NULL,
    feedback TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_answer_records_score CHECK (score >= 0 AND score <= 1),
    CONSTRAINT fk_answer_records_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_answer_records_question
        FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS wrong_questions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    question_id CHAR(36) NOT NULL,
    related_knowledge TEXT NOT NULL,
    error_count INT NOT NULL DEFAULT 1,
    last_wrong_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wrong_questions_user_question (user_id, question_id),
    CONSTRAINT fk_wrong_questions_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_wrong_questions_question
        FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS review_plans (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    weak_points JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_plans_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS review_tasks (
    id CHAR(36) PRIMARY KEY,
    plan_id CHAR(36) NOT NULL,
    day INT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    task LONGTEXT NOT NULL,
    reason LONGTEXT NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_review_tasks_day CHECK (day >= 1),
    CONSTRAINT fk_review_tasks_plan
        FOREIGN KEY (plan_id) REFERENCES review_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
