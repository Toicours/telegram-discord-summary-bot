"""
Prompt Management Module

This module provides a flexible and comprehensive system for managing 
prompting strategies across different Large Language Models (LLMs).

The design allows for:
- Context-aware prompt selection
- Easy customization
- Multiple levels of prompt override
- Support for specialized and generic prompts

Key Features:
- Topic-based prompt routing
- Explicit prompt type selection
- System and user prompt customization
- Fallback mechanisms
"""

from typing import Dict, Optional, Any

class PromptTemplates:
    """
    A sophisticated prompt management system for LLM summarization.

    This class provides a flexible mechanism for generating and customizing 
    prompts based on context, topic, and specific requirements.

    Attributes:
        DEFAULT_SYSTEM_PROMPT (str): A generic system prompt for basic summarization.
        DEFAULT_USER_PROMPT (str): A standard template for formatting user input.
        SPECIALIZED_PROMPTS (Dict[str, Dict[str, str]]): A collection of context-specific prompts.
    """

    DEFAULT_SYSTEM_PROMPT: str = """
    You are an expert summarization assistant designed to extract 
    key insights from complex conversations.

    Core Summarization Guidelines:
    1. Identify the most significant information
    2. Maintain objectivity and precision
    3. Provide clear, structured insights
    4. Focus on actionable and meaningful content
    5. Adapt to the specific context of the conversation
    """

    DEFAULT_USER_PROMPT: str = """
    Analyze and summarize the following conversation with careful attention 
    to context, key themes, and important details.

    Conversation Transcript:
    {text}

    Summary Expectations:
    - Concise yet comprehensive overview
    - Highlight main topics and notable interactions
    - Capture essential insights and potential implications
    - Maintain the original context's tone and significance
    """

    SPECIALIZED_PROMPTS: Dict[str, Dict[str, str]] = {
        'general': {
            'system_prompt': DEFAULT_SYSTEM_PROMPT,
            'user_prompt': DEFAULT_USER_PROMPT
        },
        'defi': {
            'system_prompt': """
            You are a specialized DeFi (Decentralized Finance) analyst 
            focusing on extracting critical insights from cryptocurrency 
            and blockchain-related discussions.

            Analysis Priorities:
            1. Identify yield farming opportunities
            2. Assess liquidity provision strategies
            3. Highlight market sentiment and trends
            4. Evaluate potential risks and rewards
            5. Detect emerging protocols and innovations
            """,
            'user_prompt': """
            Conduct a comprehensive analysis of the following DeFi conversation, 
            emphasizing financial strategies, market dynamics, and technological innovations.

            Conversation Transcript:
            {text}

            Detailed Analysis Requirements:
            - Extract specific financial metrics
            - Identify unique investment perspectives
            - Assess potential market impacts
            - Provide actionable insights for DeFi participants
            """
        }
    }

    @classmethod
    def get_prompts(
        cls, 
        topic_name: Optional[str] = None, 
        prompt_type: Optional[str] = None, 
        override_system_prompt: Optional[str] = None, 
        override_user_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Dynamically retrieve and customize prompts based on multiple parameters.

        This method provides a sophisticated prompt selection mechanism that:
        - Prioritizes explicit prompt type specification
        - Falls back to topic-based specialized prompts
        - Defaults to general prompts if no specific match is found
        - Allows complete prompt overriding

        Args:
            topic_name (Optional[str]): Context or topic of the conversation.
                Used to select specialized prompts if no explicit type is provided.
            
            prompt_type (Optional[str]): Explicitly specified prompt type.
                Overrides topic-based selection if provided.
            
            override_system_prompt (Optional[str]): Custom system prompt 
                that completely replaces the selected prompt's system prompt.
            
            override_user_prompt (Optional[str]): Custom user prompt 
                that completely replaces the selected prompt's user prompt.

        Returns:
            Dict[str, str]: A dictionary containing 'system_prompt' and 'user_prompt'.
                May include overridden prompts if specified.

        Examples:
            >>> prompts = PromptTemplates.get_prompts(topic_name="Yield Farming")
            >>> prompts = PromptTemplates.get_prompts(prompt_type='defi')
            >>> prompts = PromptTemplates.get_prompts(
            ...     topic_name="Bitcoin", 
            ...     override_system_prompt="You are a crypto market analyst"
            ... )
        """
        # Determine base prompts with prioritized selection
        if prompt_type and prompt_type in cls.SPECIALIZED_PROMPTS:
            # Explicit prompt type takes highest priority
            prompts = cls.SPECIALIZED_PROMPTS[prompt_type]
        elif topic_name:
            # Try to find specialized prompt based on topic
            topic_lower = topic_name.lower()
            for key, specialized_prompts in cls.SPECIALIZED_PROMPTS.items():
                if key in topic_lower:
                    prompts = specialized_prompts
                    break
            else:
                # Default to general if no match
                prompts = cls.SPECIALIZED_PROMPTS['general']
        else:
            # Fallback to general prompts
            prompts = cls.SPECIALIZED_PROMPTS['general']
        
        # Apply prompt overrides
        if override_system_prompt is not None:
            prompts['system_prompt'] = override_system_prompt
        
        if override_user_prompt is not None:
            prompts['user_prompt'] = override_user_prompt
        
        return prompts

    @classmethod
    def format_user_prompt(
        cls, 
        text: str, 
        topic_name: Optional[str] = None, 
        prompt_type: Optional[str] = None,
        override_system_prompt: Optional[str] = None,
        override_user_prompt: Optional[str] = None
    ) -> str:
        """
        Format the user prompt with the given text and optional customization.

        This method combines text formatting with prompt selection, allowing
        for dynamic and context-aware prompt generation.

        Args:
            text (str): The conversation or text to be summarized.
            
            topic_name (Optional[str]): Context or topic of the conversation.
            
            prompt_type (Optional[str]): Explicitly specified prompt type.
            
            override_system_prompt (Optional[str]): Custom system prompt.
            
            override_user_prompt (Optional[str]): Custom user prompt.

        Returns:
            str: A formatted user prompt ready for LLM submission.

        Examples:
            >>> formatted_prompt = PromptTemplates.format_user_prompt(
            ...     "Bitcoin discussion transcript", 
            ...     topic_name="Cryptocurrency"
            ... )
        """
        prompts = cls.get_prompts(
            topic_name=topic_name, 
            prompt_type=prompt_type,
            override_system_prompt=override_system_prompt,
            override_user_prompt=override_user_prompt
        )
        return prompts['user_prompt'].format(text=text)