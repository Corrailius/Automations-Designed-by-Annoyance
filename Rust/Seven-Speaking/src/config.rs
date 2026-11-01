use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub account: AccountConfig,
    pub urls: UrlConfig,
    pub language: LanguageConfig,
    pub answer_mix: AnswerMixConfig,
    pub lessons: LessonConfig,
    pub pacing: PacingConfig,
    pub delays: DelayConfig,
    pub robustness: RobustnessConfig,
}

#[derive(Debug, Deserialize)]
pub struct AccountConfig {
    pub email: String,
}

#[derive(Debug, Deserialize)]
pub struct UrlConfig {
    pub login: String,
    pub home: String,
    pub document: String,
    pub api: String,
}

#[derive(Debug, Deserialize)]
pub struct LanguageConfig {
    pub interface: String,
    pub taught: String,
}

#[derive(Debug, Deserialize)]
pub struct AnswerMixConfig {
    pub good_answers_per_cycle: u32,
    pub wrong_answers_per_cycle: u32,
}

#[derive(Debug, Deserialize)]
pub struct LessonConfig {
    pub completed_weight: f64,
}

#[derive(Debug, Deserialize)]
pub struct PacingConfig {
    pub quiz_minutes_per_10: f64,
    pub min_think_seconds: f64,
    pub max_think_seconds: f64,
    pub think_jitter: f64,
}

#[derive(Debug, Deserialize)]
pub struct DelayConfig {
    pub pause_min_seconds: f64,
    pub pause_max_seconds: f64,
    pub api_min_seconds: f64,
    pub api_max_seconds: f64,
}

#[derive(Debug, Deserialize)]
pub struct RobustnessConfig {
    pub quiz_payload_timeout: u64,
    pub max_consecutive_failures: u32,
}