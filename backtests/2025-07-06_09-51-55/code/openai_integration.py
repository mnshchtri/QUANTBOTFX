"""
OpenAI Integration for Trading System
Adds natural language processing and market analysis capabilities
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAITradingAssistant:
    """OpenAI-powered trading assistant"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI integration"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            self.enabled = True
            logger.info("OpenAI integration enabled")
        else:
            self.enabled = False
            logger.warning("OpenAI API key not found - integration disabled")
    
    def analyze_market_sentiment(self, market_data: Dict, news_headlines: List[str] = None) -> Dict:
        """Analyze market sentiment using OpenAI"""
        if not self.enabled:
            return {"sentiment": "neutral", "confidence": 0.5, "reasoning": "OpenAI not available"}
        
        try:
            # Prepare market context
            context = self._prepare_market_context(market_data, news_headlines)
            
            # Create prompt for sentiment analysis
            prompt = f"""
            Analyze the following forex market data and provide sentiment analysis:
            
            Market Data:
            {json.dumps(market_data, indent=2)}
            
            News Headlines:
            {news_headlines or ['No recent news']}
            
            Please provide:
            1. Overall sentiment (bullish/bearish/neutral)
            2. Confidence level (0-1)
            3. Key reasoning points
            4. Trading recommendations
            
            Format your response as JSON.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional forex market analyst. Provide concise, accurate analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "reasoning": f"Error: {str(e)}"}
    
    def generate_trading_insights(self, symbol: str, technical_signals: Dict, market_context: Dict) -> Dict:
        """Generate trading insights using OpenAI"""
        if not self.enabled:
            return {"insights": [], "recommendation": "HOLD"}
        
        try:
            prompt = f"""
            Analyze the following forex trading scenario:
            
            Symbol: {symbol}
            Technical Signals: {json.dumps(technical_signals, indent=2)}
            Market Context: {json.dumps(market_context, indent=2)}
            
            Provide:
            1. Key insights about the current market situation
            2. Trading recommendation (BUY/SELL/HOLD)
            3. Risk factors to consider
            4. Entry and exit points
            
            Format as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert forex trader. Provide actionable trading advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.2
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            logger.error(f"OpenAI insights generation error: {e}")
            return {"insights": [], "recommendation": "HOLD"}
    
    def analyze_news_impact(self, news_headlines: List[str], symbol: str) -> Dict:
        """Analyze news impact on currency pairs"""
        if not self.enabled:
            return {"impact": "neutral", "confidence": 0.5}
        
        try:
            prompt = f"""
            Analyze the potential impact of these news headlines on {symbol}:
            
            Headlines:
            {chr(10).join(news_headlines)}
            
            Provide:
            1. Impact assessment (positive/negative/neutral)
            2. Confidence level (0-1)
            3. Key factors driving the impact
            4. Expected market reaction
            
            Format as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a forex news analyst. Assess news impact on currency pairs."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            impact_analysis = json.loads(response.choices[0].message.content)
            return impact_analysis
            
        except Exception as e:
            logger.error(f"OpenAI news analysis error: {e}")
            return {"impact": "neutral", "confidence": 0.5}
    
    def _prepare_market_context(self, market_data: Dict, news_headlines: List[str]) -> str:
        """Prepare market context for OpenAI analysis"""
        context = {
            "current_price": market_data.get("price", 0),
            "technical_indicators": {
                "rsi": market_data.get("rsi", 50),
                "ema_ratio": market_data.get("ema_ratio", 1.0),
                "volatility": market_data.get("volatility", 0.0)
            },
            "recent_movement": market_data.get("returns_1d", 0),
            "volume_ratio": market_data.get("volume_ratio", 1.0)
        }
        
        return json.dumps(context, indent=2)

class EnhancedForexStrategy:
    """Forex strategy enhanced with OpenAI capabilities"""
    
    def __init__(self):
        self.openai_assistant = OpenAITradingAssistant()
        self.sentiment_cache = {}
        self.insights_cache = {}
    
    def generate_enhanced_signal(self, symbol: str, technical_data: Dict, 
                                news_headlines: List[str] = None) -> Dict:
        """Generate enhanced trading signal with OpenAI analysis"""
        
        # Get technical signal (existing logic)
        technical_signal = self._generate_technical_signal(technical_data)
        
        # Get OpenAI sentiment analysis
        sentiment = self.openai_assistant.analyze_market_sentiment(
            technical_data, news_headlines
        )
        
        # Get OpenAI trading insights
        insights = self.openai_assistant.generate_trading_insights(
            symbol, technical_signal, {"sentiment": sentiment}
        )
        
        # Combine technical and AI analysis
        final_signal = self._combine_signals(technical_signal, sentiment, insights)
        
        return {
            "symbol": symbol,
            "technical_signal": technical_signal,
            "sentiment_analysis": sentiment,
            "ai_insights": insights,
            "final_signal": final_signal,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_technical_signal(self, data: Dict) -> Dict:
        """Generate technical trading signal"""
        # Simplified technical analysis
        rsi = data.get("rsi", 50)
        ema_ratio = data.get("ema_ratio", 1.0)
        volatility = data.get("volatility", 0.0)
        
        score = 0.0
        
        # RSI rules
        if rsi < 30:
            score += 0.3
        elif rsi > 70:
            score -= 0.3
        
        # EMA rules
        if ema_ratio > 1.01:
            score += 0.2
        elif ema_ratio < 0.99:
            score -= 0.2
        
        # Determine signal
        if score > 0.3:
            signal = "BUY"
        elif score < -0.3:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return {
            "signal": signal,
            "confidence": min(abs(score), 0.9),
            "score": score
        }
    
    def _combine_signals(self, technical: Dict, sentiment: Dict, insights: Dict) -> Dict:
        """Combine technical and AI signals"""
        tech_signal = technical["signal"]
        tech_confidence = technical["confidence"]
        
        sentiment_score = 0.0
        if sentiment.get("sentiment") == "bullish":
            sentiment_score = 0.3
        elif sentiment.get("sentiment") == "bearish":
            sentiment_score = -0.3
        
        ai_recommendation = insights.get("recommendation", "HOLD")
        
        # Combine signals
        final_score = tech_confidence + sentiment_score
        
        if final_score > 0.4:
            final_signal = "BUY"
        elif final_score < -0.4:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
        
        return {
            "signal": final_signal,
            "confidence": min(abs(final_score), 0.9),
            "technical_weight": 0.6,
            "sentiment_weight": 0.4,
            "ai_recommendation": ai_recommendation
        }

def main():
    """Demo OpenAI integration"""
    print("🤖 OpenAI Trading Integration Demo")
    print("=" * 40)
    
    # Create enhanced strategy
    strategy = EnhancedForexStrategy()
    
    # Sample market data
    market_data = {
        "price": 1.1000,
        "rsi": 65,
        "ema_ratio": 1.02,
        "volatility": 0.015,
        "returns_1d": 0.002,
        "volume_ratio": 1.2
    }
    
    # Sample news headlines
    news_headlines = [
        "ECB signals potential rate cut in next meeting",
        "US Dollar strengthens against major currencies",
        "Euro zone inflation data shows mixed signals"
    ]
    
    # Generate enhanced signal
    result = strategy.generate_enhanced_signal("EURUSD", market_data, news_headlines)
    
    print(f"Symbol: {result['symbol']}")
    print(f"Technical Signal: {result['technical_signal']['signal']}")
    print(f"Sentiment: {result['sentiment_analysis'].get('sentiment', 'neutral')}")
    print(f"AI Recommendation: {result['final_signal']['ai_recommendation']}")
    print(f"Final Signal: {result['final_signal']['signal']}")
    print(f"Confidence: {result['final_signal']['confidence']:.2f}")

if __name__ == "__main__":
    main() 