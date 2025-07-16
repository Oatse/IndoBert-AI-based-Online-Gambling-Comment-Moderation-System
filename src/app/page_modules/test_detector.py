#!/usr/bin/env python3
"""
Test Detector Page Module
Handles spam detector testing functionality
"""

import streamlit as st
import pandas as pd
from typing import List, Dict


class TestDetectorPage:
    """Handles test detector page rendering and functionality"""
    
    def __init__(self, spam_detector, confidence_threshold: float):
        self.spam_detector = spam_detector
        self.confidence_threshold = confidence_threshold
    
    def render(self):
        """Render spam detector test page"""
        # Use isolated container with unique key to prevent bleeding
        test_detector_key = "test_detector_main_container"

        # Clear any existing test detector state to prevent bleeding
        if f"{test_detector_key}_state" in st.session_state:
            del st.session_state[f"{test_detector_key}_state"]

        test_detector_container = st.container(key=test_detector_key)
        with test_detector_container:
            st.markdown("### 🧪 Test Spam Detector")

            if not self.spam_detector:
                st.warning("⚠️ Spam detector not loaded.")
                st.info("💡 The spam detector will be loaded automatically when the model is available.")
                st.markdown("---")
                st.markdown("#### 📋 Test Interface Preview")
                st.text_area("Test Text (Preview)", placeholder="Enter comment text to test for spam detection...", disabled=True)
                st.slider("Confidence Threshold (Preview)", 0.0, 1.0, 0.5, disabled=True)
                st.button("🔍 Test Detection (Disabled)", disabled=True)
                return

            # Test input
            st.markdown("#### Enter text to test:")
            test_text = st.text_area(
                "Test Text",
                placeholder="Enter comment text to test for spam detection...",
                height=100
            )

            # Confidence threshold
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=self.confidence_threshold,
                step=0.05,
                help="Minimum confidence required to classify as spam"
            )

            if st.button("🔍 Test Detection", type="primary"):
                if test_text.strip():
                    with st.spinner("Analyzing text..."):
                        try:
                            prediction = self.spam_detector.predict(test_text)

                            # Display results
                            st.markdown("#### 📊 Detection Results")

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                label = prediction['label']
                                emoji = "🚨" if prediction['is_spam'] else "✅"
                                st.metric("Classification", f"{emoji} {label.upper()}")

                            with col2:
                                confidence = prediction['confidence']
                                st.metric("Confidence", f"{confidence:.3f}")

                            with col3:
                                is_spam_threshold = prediction['is_spam'] and confidence > confidence_threshold
                                action = "DELETE" if is_spam_threshold else "KEEP"
                                color = "🔴" if is_spam_threshold else "🟢"
                                st.metric("Action", f"{color} {action}")

                            # Detailed information
                            st.markdown("#### 📋 Detailed Information")
                            st.json(prediction)

                            # Explanation
                            if prediction['is_spam']:
                                if confidence > confidence_threshold:
                                    st.error(f"🚨 This comment would be **DELETED** (confidence {confidence:.3f} > threshold {confidence_threshold})")
                                else:
                                    st.warning(f"⚠️ Detected as spam but confidence {confidence:.3f} is below threshold {confidence_threshold}")
                            else:
                                st.success("✅ This comment would be **KEPT** (classified as normal)")

                        except Exception as e:
                            st.error(f"❌ Error testing detection: {str(e)}")
                else:
                    st.warning("Please enter some text to test.")

            # Batch testing
            st.markdown("---")
            st.markdown("#### 📝 Batch Testing")

            batch_text = st.text_area(
                "Batch Test (one comment per line)",
                placeholder="Enter multiple comments, one per line...",
                height=150
            )

            if st.button("🔍 Test Batch", type="secondary"):
                if batch_text.strip():
                    lines = [line.strip() for line in batch_text.split('\n') if line.strip()]

                    if lines:
                        with st.spinner(f"Testing {len(lines)} comments..."):
                            results = self._process_batch_test(lines, confidence_threshold)

                            # Display results table
                            df = pd.DataFrame(results)
                            st.dataframe(
                                df[['text', 'label', 'confidence', 'action']],
                                use_container_width=True
                            )

                            # Summary
                            spam_count = sum(1 for r in results if r['is_spam'] and r['confidence'] > confidence_threshold)
                            st.info(f"📊 Summary: {spam_count} out of {len(results)} comments would be deleted as spam")

    def _process_batch_test(self, lines: List[str], confidence_threshold: float) -> List[Dict]:
        """Process batch testing of multiple comments"""
        results = []

        for line in lines:
            try:
                prediction = self.spam_detector.predict(line)
                results.append({
                    'text': line[:50] + "..." if len(line) > 50 else line,
                    'full_text': line,
                    'is_spam': prediction['is_spam'],
                    'confidence': prediction['confidence'],
                    'label': prediction['label'],
                    'action': 'DELETE' if prediction['is_spam'] and prediction['confidence'] > confidence_threshold else 'KEEP'
                })
            except Exception as e:
                results.append({
                    'text': line[:50] + "..." if len(line) > 50 else line,
                    'full_text': line,
                    'is_spam': False,
                    'confidence': 0.0,
                    'label': 'error',
                    'action': 'ERROR',
                    'error': str(e)
                })

        return results
