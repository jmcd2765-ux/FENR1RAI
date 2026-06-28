# Configuration & Best Practices Guide

## Mood Engine Tuning

### Conservative (Stable) Mode
```python
# In Mood/mood_tracker.py __init__
self.mood_decay_rate = 0.01      # Very slow fade
self.mood_inertia = 3.0          # Hard to shift mood
self.mood_strength = 0.5         # Moderate base strength
```
**Use case**: Want bot to stay in consistent emotional state, less reactivity

### Reactive (Expressive) Mode
```python
self.mood_decay_rate = 0.03      # Fast emotional fade
self.mood_inertia = 1.0          # Easy to shift mood
self.mood_strength = 0.7         # Higher starting strength
```
**Use case**: Want bot to respond quickly to chat emotions, more dramatic

### Balanced (Recommended) Mode
```python
self.mood_decay_rate = 0.02      # Moderate fade
self.mood_inertia = 2.0          # Normal sensitivity
self.mood_strength = 0.5         # Standard strength
```
**Use case**: Default, good for most streams

## Speech Pattern Configuration

### Minimal Pattern Matching
```python
# In speech_pattern_analyzer.py
# Change minimum samples threshold in get_pattern_injection()
if profile["message_count"] < 10:  # Require more samples
    return ""
```
**Use case**: Only match patterns for regular chatters, reduce noise

### Aggressive Pattern Matching
```python
if profile["message_count"] < 2:  # Apply patterns early
    return ""
```
**Use case**: Want bot to adapt quickly to new users

### Alpha-Only Pattern Focus
```python
# In personality_engine.py _system_prompt()
# Remove generic user patterns, keep only Alpha
if username != alpha_channel_name:
    pattern_injection = ""
```
**Use case**: Only match Alpha's patterns, ignore other users

## Response Quality Configuration

### Length Constraints
```python
# In response_quality_enhancer.py _trim_response()
max_length = 220        # Twitch max
max_length = 150        # For shorter messages
max_length = 100        # For quick reactions
```

### Emoji Usage
```python
# In response_quality_enhancer.py _apply_pattern_matching()
# Add this to always include emoji if user does
if emoji_count > 0 and len(response) < 180:
    response += f" {emoji_to_add}"
```

### Capitalization Matching
```python
# More aggressive cap style matching
if cap_style == "lowercase":
    response = response.lower()
elif cap_style == "UPPERCASE":
    response = response.upper()
```

## Learning Engine Configuration

### Sentiment Sensitivity
```python
# In learning.py _update_sentiment_trend()
sentiment_score += 0.5  # More aggressive scoring
sentiment_score += 0.1  # Less aggressive scoring
```

### Communication Style Weights
```python
# In learning.py _analyze_communication_style()
profile["communication_style"][f"length_{category}"] += 1  # Current
profile["communication_style"][f"length_{category}"] += 3  # More weight
```

## Temperature Mapping Customization

### Creative Mode
```python
# In personality_engine.py _call_ollama()
mood_temperature_map = {
    "happy": 0.95,      # Very creative
    "sad": 0.75,
    "angry": 0.85,
    "neutral": 0.85
}
```

### Conservative Mode
```python
mood_temperature_map = {
    "happy": 0.75,      # Less random
    "sad": 0.65,
    "angry": 0.70,
    "neutral": 0.75
}
```

### Personality-Specific
```python
mood_temperature_map = {
    "happy": 0.9,       # Playful, energetic
    "sad": 0.65,        # Thoughtful, careful
    "angry": 0.7,       # Sharp, witty
    "neutral": 0.8      # Balanced
}
```

## Monitoring & Logging

### Enable Detailed Debug Logs
```python
# In main.py or config
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_debug.log'),
        logging.StreamHandler()
    ]
)
```

### Watch Specific Components
```python
# In logging
import logging
logging.getLogger('personality_engine').setLevel(logging.DEBUG)
logging.getLogger('Mood.mood_tracker').setLevel(logging.DEBUG)
logging.getLogger('speech_pattern_analyzer').setLevel(logging.DEBUG)
```

## Performance Tuning

### Reduce Memory Usage
```python
# In speech_pattern_analyzer.py analyze_message()
if len(profile["samples"]) > 50:  # Was 100
    profile["samples"] = profile["samples"][-50:]

# In Mood/mood_tracker.py set_mood()
if len(self.mood_triggers_history) > 20:  # Was 50
    self.mood_triggers_history = self.mood_triggers_history[-20:]
```

### Reduce LLM Token Usage
```python
# In personality_engine.py _build_messages()
# Limit pattern injection length
if len(pattern_injection) > 100:
    pattern_injection = pattern_injection[:100] + "..."

# Limit mood context
if len(mood_context) > 80:
    # Use shorter version
    mood_context = f"Mood: {mood.name}"
```

## Stream-Specific Configurations

### Gaming Streams
```python
# Emphasis on game-specific mood triggers
# In Mood/mood_tracker.py observe_chat()
game_victory_words = ["won", "victory", "clutch", "ace", "penta", "gg"]
game_loss_words = ["lost", "death", "rip", "ff", "surrender"]

if any(word in text for word in game_victory_words):
    mood_trigger = "happy"
    intensity = 0.8
```

### Chill/Hangout Streams
```python
# Emphasis on social mood triggers
social_words = ["friends", "community", "love", "family", "together"]

if any(word in text for word in social_words):
    mood_trigger = "happy"
    intensity = 0.6
```

### Competitive Streams
```python
# Emphasis on intense mood triggers
competitive_words = ["tryhard", "sweat", "ranked", "tournament", "clutch"]

if any(word in text for word in competitive_words):
    mood_trigger = "angry"  # Competitive energy
    intensity = 0.7
```

## Alpha Integration

### Heavy Alpha Bias
```python
# In Mood/mood_tracker.py set_mood()
if from_alpha:
    intensity = min(1.0, intensity * 2.0)  # Was 1.5
```

### Alpha Pattern Priority
```python
# In personality_engine.py _system_prompt()
# Ensure Alpha's pattern is first/dominant
if alpha_pattern:
    prompt_parts.insert(0, alpha_pattern)  # Top priority
```

## Debugging Checklist

- [ ] Verify speech patterns are being collected (`get_user_pattern_summary()`)
- [ ] Check mood state is changing (`get_mood_stability_report()`)
- [ ] Confirm learning profiles are updating (`get_user_context()`)
- [ ] Test response enhancement works (`enhance_response()`)
- [ ] Validate security filter doesn't block good responses
- [ ] Monitor temperature values match mood expectations
- [ ] Check token count in prompts (balance and quality)
- [ ] Verify Alpha's patterns are being used

## Common Customizations

### 1. Add Game-Specific Moods
```python
# In Mood/mood_tracker.py observe_chat()
if "pokemon" in text and "shiny" in text:
    mood_trigger = "happy"
    intensity = 0.9
```

### 2. Add User-Specific Patterns
```python
# In speech_pattern_analyzer.py
# Add special handling for specific users
if username == "special_user":
    # Store patterns differently
    # Apply patterns more aggressively
```

### 3. Add Custom Sentiment Triggers
```python
# In learning.py _update_sentiment_trend()
custom_positive = ["poggers", "based", "big brain"]
custom_negative = ["cringe", "yikes", "fail"]

for word in custom_positive:
    if word in content_lower:
        sentiment_score += 0.4
```

### 4. Add Time-Based Moods
```python
# In Mood/mood_tracker.py observe_chat()
from datetime import datetime
hour = datetime.now().hour

if hour >= 22 or hour < 8:  # Late night
    mood_inertia = 1.0  # Easier to shift to tired/chill mood
```

## Performance Monitoring

### Track Enhancement Performance
```python
# In response_quality_enhancer.py enhance_response()
import time
start = time.time()
enhanced = self._apply_mood_adjustments(enhanced)
enhanced = self._apply_pattern_matching(enhanced, user_name)
elapsed = time.time() - start
print(f"Enhancement took {elapsed*1000:.2f}ms")
```

### Monitor Mood Transitions
```python
# In Mood/mood_tracker.py set_mood()
self.logger.info(
    f"Mood: {old_mood}→{mood_name}, "
    f"strength={self.mood_strength:.2f}, "
    f"signals={self.conflicting_signals:.1f}/{self.mood_inertia}"
)
```

---

## Recommended Starting Configuration

```python
# Conservative but responsive
mood_decay_rate = 0.02
mood_inertia = 2.0
pattern_sample_threshold = 5
response_max_length = 220
temperature_happy = 0.85
temperature_sad = 0.7
temperature_angry = 0.75
temperature_neutral = 0.8
alpha_weight = 1.5
```

## Quick Adjustment Guide

| Problem | Adjustment |
|---------|------------|
| Bot too emotional | Increase mood_inertia, decrease decay_rate |
| Bot too stable | Decrease mood_inertia, increase decay_rate |
| Responses too generic | Lower pattern_sample_threshold |
| Responses don't match mood | Check temperature map, ensure mood is changing |
| Responses too long | Lower response_max_length |
| Alpha not prioritized | Check alpha_weight multiplier |
| Too many tokens to LLM | Limit pattern_injection length, use shorter contexts |

---

*These configurations allow fine-tuning the bot's personality and responsiveness to match your stream's vibe.*
