"""
Test Redis connection and caching operations
"""
# ruff: noqa: E402

import os
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import redis
from dotenv import load_dotenv

load_dotenv('.env.dev')


def test_redis_operations() -> bool:
    """Test Redis with various operations"""
    print("="*60)
    print("Redis Connection & Operations Test")
    print("="*60)
    
    try:
        # Connect to Redis
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
        print("\n→ Test 1: Connection")
        r.ping()
        print("✓ Connected to Redis")
        
        # Test 2: String operations
        print("\n→ Test 2: String operations")
        r.set('test:string', 'Hello Redis')
        value = r.get('test:string')
        assert value == 'Hello Redis', "String value mismatch"
        print(f"✓ String set/get successful: {value}")
        
        # Test 3: TTL (expiration)
        print("\n→ Test 3: TTL (expiration)")
        r.set('test:ttl', 'expires soon', ex=2)
        ttl = r.ttl('test:ttl')
        print(f"✓ TTL set successfully: {ttl} seconds")
        
        time.sleep(3)
        value = r.get('test:ttl')
        assert value is None, "TTL did not expire"
        print("✓ TTL expiration works correctly")
        
        # Test 4: Hash operations
        print("\n→ Test 4: Hash operations")
        r.hset('test:hash', mapping={
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        })
        
        hash_value = r.hgetall('test:hash')
        assert len(hash_value) == 3, "Hash size mismatch"
        print(f"✓ Hash operations successful: {len(hash_value)} fields")
        
        # Test 5: List operations
        print("\n→ Test 5: List operations")
        r.lpush('test:list', 'item1', 'item2', 'item3')
        list_len = r.llen('test:list')
        assert list_len == 3, "List length mismatch"
        print(f"✓ List operations successful: {list_len} items")
        
        # Test 6: Set operations
        print("\n→ Test 6: Set operations")
        r.sadd('test:set', 'member1', 'member2', 'member3')
        set_size = r.scard('test:set')
        assert set_size == 3, "Set size mismatch"
        print(f"✓ Set operations successful: {set_size} members")
        
        # Test 7: Sorted set operations
        print("\n→ Test 7: Sorted set operations")
        r.zadd('test:zset', {'item1': 1.0, 'item2': 2.0, 'item3': 3.0})
        zset_size = r.zcard('test:zset')
        assert zset_size == 3, "Sorted set size mismatch"
        print(f"✓ Sorted set operations successful: {zset_size} members")
        
        # Test 8: Increment/Decrement
        print("\n→ Test 8: Counter operations")
        r.set('test:counter', 0)
        r.incr('test:counter')
        r.incrby('test:counter', 5)
        counter = int(r.get('test:counter'))
        assert counter == 6, "Counter value mismatch"
        print(f"✓ Counter operations successful: {counter}")
        
        # Test 9: Pipeline (atomic operations)
        print("\n→ Test 9: Pipeline operations")
        pipe = r.pipeline()
        pipe.set('test:pipe1', 'value1')
        pipe.set('test:pipe2', 'value2')
        pipe.set('test:pipe3', 'value3')
        results = pipe.execute()
        assert len(results) == 3, "Pipeline execution mismatch"
        print(f"✓ Pipeline successful: {len(results)} operations executed")
        
        # Test 10: Key pattern matching
        print("\n→ Test 10: Key pattern matching")
        keys = r.keys('test:*')
        print(f"✓ Pattern matching successful: {len(keys)} keys found")
        
        # Cleanup
        print("\n→ Cleanup: Removing test keys")
        for key in r.keys('test:*'):
            r.delete(key)
        remaining = r.keys('test:*')
        assert len(remaining) == 0, "Cleanup incomplete"
        print("✓ Cleanup successful")
        
        # Memory info
        print("\n→ Redis Server Info")
        info = r.info()
        print(f"  Redis Version: {info['redis_version']}")
        print(f"  Memory Used: {info['used_memory_human']}")
        print(f"  Connected Clients: {info['connected_clients']}")
        print(f"  Total Commands: {info['total_commands_processed']}")
        
        print("\n" + "="*60)
        print("✓ All Redis tests passed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ Redis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_redis_operations()
    sys.exit(0 if success else 1)