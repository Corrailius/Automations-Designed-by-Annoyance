use crate::config::Config;

pub fn validate(config: &Config) -> Result<(), String> {
    validate_pacing(config)?;
    validate_delays(config)?;
    validate_lessons(config)?;
    validate_answer_mix(config)?;
    validate_robustness(config)?;

    Ok(())
}

fn validate_pacing(config: &Config) -> Result<(), String> {
    let pacing = &config.pacing;

    if !pacing.quiz_minutes_per_10.is_finite()
        || pacing.quiz_minutes_per_10 < 0.0
    {
        return Err("Quiz minutes per 10 must be finite and non-negative.".into());
    }

    if !pacing.min_think_seconds.is_finite()
        || !pacing.max_think_seconds.is_finite()
        || pacing.min_think_seconds < 0.0
        || pacing.max_think_seconds < 0.0
    {
        return Err("Thinking times must be finite and non-negative.".into());
    }

    if pacing.min_think_seconds > pacing.max_think_seconds {
        return Err("Minimum thinking time cannot exceed maximum thinking time.".into());
    }

    if !pacing.think_jitter.is_finite() || pacing.think_jitter < 0.0 {
        return Err("Thinking jitter must be finite and non-negative.".into());
    }

    Ok(())
}

fn validate_delays(config: &Config) -> Result<(), String> {
    let delays = &config.delays;

    let values = [
        delays.pause_min_seconds,
        delays.pause_max_seconds,
        delays.api_min_seconds,
        delays.api_max_seconds,
    ];

    if values.iter().any(|value| !value.is_finite() || *value < 0.0) {
        return Err("All delays must be finite and non-negative.".into());
    }

    if delays.pause_min_seconds > delays.pause_max_seconds {
        return Err("Minimum activity pause cannot exceed maximum activity pause.".into());
    }

    if delays.api_min_seconds > delays.api_max_seconds {
        return Err("Minimum API delay cannot exceed maximum API delay.".into());
    }

    Ok(())
}

fn validate_lessons(config: &Config) -> Result<(), String> {
    let weight = config.lessons.completed_weight;

    if !weight.is_finite() || weight < 0.0 {
        return Err("Completed lesson weight must be finite and non-negative.".into());
    }

    Ok(())
}

fn validate_answer_mix(config: &Config) -> Result<(), String> {
    let answers = &config.answer_mix;

    if answers.good_answers_per_cycle == 0
        && answers.wrong_answers_per_cycle == 0
    {
        return Err("The answer cycle must contain at least one answer.".into());
    }

    Ok(())
}

fn validate_robustness(config: &Config) -> Result<(), String> {
    if config.robustness.quiz_payload_timeout == 0 {
        return Err("Quiz payload timeout must be greater than zero.".into());
    }

    if config.robustness.max_consecutive_failures == 0 {
        return Err("Maximum consecutive failures must be greater than zero.".into());
    }

    Ok(())
}