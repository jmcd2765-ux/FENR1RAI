#!/usr/bin/env python3
"""
Verification script for FENR1R bot enhancements.
Tests that all new modules work and are properly integrated.
"""

import sys
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all new modules can be imported."""
    logger.info("Testing imports...")
    
    modules_to_test = [
        ("speech_pattern_analyzer", "SpeechPatternAnalyzer"),
        ("response_quality_enhancer", "ResponseQualityEnhancer"),
        ("learning", "LearningEngine"),
        ("Mood.mood_tracker", "MoodEngine"),
        ("personality_engine", "PersonalityEngine"),
        ("twitch_bot", "FENR1RBot"),
    ]
    
    failed = []
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name, None)
            if cls is None:
                failed.append(f"{module_name}: Class {class_name} not found")
            else:
                logger.info(f"✓ {module_name}.{class_name}")
        except Exception as e:
            failed.append(f"{module_name}: {str(e)}")
    
    if failed:
        logger.error("Import failures:")
        for f in failed:
            logger.error(f"  ✗ {f}")
        return False
    
    logger.info("✓ All imports successful")
    return True

def test_speech_analyzer():
    """Test speech pattern analyzer."""
    logger.info("\nTesting SpeechPatternAnalyzer...")
    
    try:
        from speech_pattern_analyzer import SpeechPatternAnalyzer
        
        analyzer = SpeechPatternAnalyzer()
        
        # Test message analysis
        analyzer.analyze_message("testuser", "OMG YES! That's so awesome!! 🎉", is_alpha=False)
        analyzer.analyze_message("testuser", "lol yeah that was cool")
        analyzer.analyze_message("testuser", "I love this! 🎮")
        
        # Test pattern summary
        summary = analyzer.get_user_pattern_summary("testuser")
        if not summary:
            logger.error("✗ Pattern summary empty")
            return False
        
        logger.info(f"✓ Pattern summary generated: {len(summary)} chars")
        
        # Test Alpha instruction
        analyzer.analyze_message("alpha", "streamer messages", is_alpha=True)
        alpha_instr = analyzer.get_alpha_instruction()
        if not alpha_instr or alpha_instr.startswith("Emulate"):
            logger.info("✓ Alpha instruction generated")
        
        return True
    except Exception as e:
        logger.error(f"✗ SpeechPatternAnalyzer test failed: {e}")
        return False

def test_mood_engine():
    """Test enhanced mood engine."""
    logger.info("\nTesting MoodEngine...")
    
    try:
        from Mood.mood_tracker import MoodEngine
        
        mood = MoodEngine()
        
        # Test mood observation
        mood.observe_chat("user1", "I love this!", tags=None)
        if mood.current_mood.name != "happy":
            logger.error(f"✗ Expected happy mood, got {mood.current_mood.name}")
            return False
        logger.info(f"✓ Mood correctly set to: {mood.current_mood.name}")
        
        # Test mood decay exists
        if not hasattr(mood, 'mood_decay_rate'):
            logger.error("✗ mood_decay_rate attribute missing")
            return False
        logger.info("✓ Mood decay rate configured")
        
        # Test emotional inertia exists
        if not hasattr(mood, 'mood_inertia'):
            logger.error("✗ mood_inertia attribute missing")
            return False
        logger.info("✓ Emotional inertia configured")
        
        # Test mood strength
        if not hasattr(mood, 'mood_strength'):
            logger.error("✗ mood_strength attribute missing")
            return False
        logger.info(f"✓ Mood strength: {mood.mood_strength:.2f}")
        
        # Test stability report
        report = mood.get_mood_stability_report()
        if not report or "Mood Stability" not in report:
            logger.error("✗ Mood stability report invalid")
            return False
        logger.info("✓ Mood stability report generated")
        
        return True
    except Exception as e:
        logger.error(f"✗ MoodEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_learning_engine():
    """Test enhanced learning engine."""
    logger.info("\nTesting LearningEngine...")
    
    try:
        from learning import LearningEngine
        
        learning = LearningEngine()
        
        # Test message observation
        learning.observe_message("testuser", "OMG valorant was insane! 🎮", tags={"subscriber": True})
        
        # Test context generation
        context = learning.get_user_context("testuser")
        if not context or "testuser" not in context:
            logger.error("✗ User context invalid")
            return False
        logger.info(f"✓ User context generated: {len(context)} chars")
        
        # Test sentiment tracking
        if "sentiment_trend" not in learning.user_profiles["testuser"]:
            logger.error("✗ sentiment_trend missing")
            return False
        logger.info("✓ Sentiment trend tracking enabled")
        
        # Test communication style
        if "communication_style" not in learning.user_profiles["testuser"]:
            logger.error("✗ communication_style missing")
            return False
        logger.info("✓ Communication style tracking enabled")
        
        return True
    except Exception as e:
        logger.error(f"✗ LearningEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_enhancer():
    """Test response quality enhancer."""
    logger.info("\nTesting ResponseQualityEnhancer...")
    
    try:
        from response_quality_enhancer import ResponseQualityEnhancer
        from Mood.mood_tracker import MoodEngine
        from speech_pattern_analyzer import SpeechPatternAnalyzer
        
        mood = MoodEngine()
        analyzer = SpeechPatternAnalyzer()
        enhancer = ResponseQualityEnhancer(mood, analyzer)
        
        # Test response enhancement
        original = "That was a cool move."
        enhanced = enhancer.enhance_response(original, "testuser")
        
        if not enhanced or len(enhanced) < 5:
            logger.error("✗ Response enhancement failed")
            return False
        logger.info(f"✓ Response enhanced: '{original}' -> '{enhanced}'")
        
        # Test validation
        if not enhancer.validate_response("This is a valid response"):
            logger.error("✗ Valid response rejected")
            return False
        logger.info("✓ Response validation working")
        
        # Test trim function
        long_response = "a" * 500
        trimmed = enhancer._trim_response(long_response, max_length=220)
        if len(trimmed) > 220:
            logger.error(f"✗ Response not trimmed: {len(trimmed)} > 220")
            return False
        logger.info(f"✓ Response trimmed correctly: {len(trimmed)} chars")
        
        return True
    except Exception as e:
        logger.error(f"✗ ResponseQualityEnhancer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_personality_engine():
    """Test personality engine integration."""
    logger.info("\nTesting PersonalityEngine...")
    
    try:
        from personality_engine import PersonalityEngine
        from config import Config
        
        config = Config()
        engine = PersonalityEngine(config=config)
        
        # Test speech analyzer integration
        if not hasattr(engine, 'speech_analyzer'):
            logger.error("✗ speech_analyzer not integrated")
            return False
        logger.info("✓ Speech analyzer integrated")
        
        # Test system prompt generation
        prompt = engine._system_prompt()
        if not prompt or "FENR1R" not in prompt:
            logger.error("✗ System prompt invalid")
            return False
        logger.info(f"✓ System prompt generated: {len(prompt)} chars")
        
        # Test message building
        messages = engine._build_messages("test message", [], user_name="testuser")
        if not messages or len(messages) < 2:
            logger.error("✗ Message building failed")
            return False
        logger.info(f"✓ Messages built: {len(messages)} messages")
        
        return True
    except Exception as e:
        logger.error(f"✗ PersonalityEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all verification tests."""
    logger.info("=" * 60)
    logger.info("FENR1R Bot Enhancement Verification")
    logger.info("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("SpeechPatternAnalyzer", test_speech_analyzer),
        ("MoodEngine", test_mood_engine),
        ("LearningEngine", test_learning_engine),
        ("ResponseQualityEnhancer", test_response_enhancer),
        ("PersonalityEngine", test_personality_engine),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("\n✓ All enhancements verified successfully!")
        logger.info("Bot is ready for deployment.")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed.")
        logger.error("Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
