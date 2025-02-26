from opto.trainer.guide import ReferenceGuide, KeywordGuide, AutoGuide, VerbalGuide

def test_auto_guide_build():
    # Test building ReferenceGuide with model parameter
    reference_guide = AutoGuide.build(model="gpt-4")
    assert isinstance(reference_guide, ReferenceGuide)
    assert reference_guide.model == "gpt-4"
    
    # Test building ReferenceGuide with custom prompt template
    custom_prompt_guide = AutoGuide.build(
        model="gpt-3.5-turbo",
        prompt_template="Custom prompt: {content}, Reference: {reference}"
    )
    assert isinstance(custom_prompt_guide, ReferenceGuide)
    assert custom_prompt_guide.model == "gpt-3.5-turbo"
    assert custom_prompt_guide.prompt_template == "Custom prompt: {content}, Reference: {reference}"
    
    # Test building KeywordGuide with keyword_response
    keyword_response = {"error": "There's an error", "warning": "There's a warning"}
    keyword_guide = AutoGuide.build(keyword_response=keyword_response)
    assert isinstance(keyword_guide, KeywordGuide)
    assert keyword_guide.keyword_response == keyword_response
    
    # Test building KeywordGuide with custom analyzers
    def custom_analyzer(content, reference_log):
        return "Custom analysis result"
    
    analyzer_guide = AutoGuide.build(
        keyword_response={"key": "value"},
        custom_analyzers=[custom_analyzer]
    )
    assert isinstance(analyzer_guide, KeywordGuide)
    assert len(analyzer_guide.custom_analyzers) == 1
    assert analyzer_guide.custom_analyzers[0](None, None) == "Custom analysis result"

test_auto_guide_build()