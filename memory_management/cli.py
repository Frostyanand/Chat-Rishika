"""
Command-line interface for the Elysia memory management system.

This module provides a command-line interface for interacting with the
memory management system.
"""
import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List, Optional

from . import initialize, get_memory_store, __version__, reset
from .config import get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up the argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Elysia Memory Management System',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'Elysia Memory Management v{__version__}'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Initialize parser
    init_parser = subparsers.add_parser('init', help='Initialize the memory system')
    init_parser.add_argument(
        '--store-type',
        choices=['json'],
        help='Type of memory store to use'
    )
    init_parser.add_argument(
        '--max-messages', type=int,
        help='Maximum number of messages to store'
    )
    init_parser.add_argument(
        '--data-dir',
        help='Directory for storing JSON data'
    )
    
    # Reset parser
    reset_parser = subparsers.add_parser('reset', help='Reset the memory system')
    reset_parser.add_argument(
        '--keep-data', action='store_true',
        help='Keep existing data during reset'
    )
    
    # User management parsers
    user_parser = subparsers.add_parser('user', help='User management commands')
    user_subparsers = user_parser.add_subparsers(dest='user_command', help='User command to execute')
    
    # Create user
    create_user_parser = user_subparsers.add_parser('create', help='Create a new user')
    create_user_parser.add_argument(
        'user_id', help='User ID'
    )
    create_user_parser.add_argument(
        '--username',
        help='Username'
    )
    
    # Get user
    get_user_parser = user_subparsers.add_parser('get', help='Get user information')
    get_user_parser.add_argument(
        'user_id', help='User ID'
    )
    
    # Delete user
    delete_user_parser = user_subparsers.add_parser('delete', help='Delete a user')
    delete_user_parser.add_argument(
        'user_id', help='User ID'
    )
    
    # Update profile
    update_profile_parser = user_subparsers.add_parser('update-profile', help='Update user profile')
    update_profile_parser.add_argument(
        'user_id', help='User ID'
    )
    update_profile_parser.add_argument(
        '--name',
        help='User name'
    )
    update_profile_parser.add_argument(
        '--timezone',
        help='User timezone'
    )
    update_profile_parser.add_argument(
        '--preferences',
        help='User preferences (JSON string)'
    )
    
    # Message management parsers
    message_parser = subparsers.add_parser('message', help='Message management commands')
    message_subparsers = message_parser.add_subparsers(dest='message_command', help='Message command to execute')
    
    # Add message
    add_message_parser = message_subparsers.add_parser('add', help='Add a message')
    add_message_parser.add_argument(
        'user_id', help='User ID'
    )
    add_message_parser.add_argument(
        'role', choices=['user', 'assistant', 'system'],
        help='Message role'
    )
    add_message_parser.add_argument(
        'content', help='Message content'
    )
    add_message_parser.add_argument(
        '--metadata',
        help='Message metadata (JSON string)'
    )
    
    # Get message history
    get_messages_parser = message_subparsers.add_parser('get', help='Get message history')
    get_messages_parser.add_argument(
        'user_id', help='User ID'
    )
    get_messages_parser.add_argument(
        '--limit', type=int,
        help='Maximum number of messages to retrieve'
    )
    
    # Fact management parsers
    fact_parser = subparsers.add_parser('fact', help='Fact management commands')
    fact_subparsers = fact_parser.add_subparsers(dest='fact_command', help='Fact command to execute')
    
    # Add fact
    add_fact_parser = fact_subparsers.add_parser('add', help='Add a fact')
    add_fact_parser.add_argument(
        'user_id', help='User ID'
    )
    add_fact_parser.add_argument(
        'fact', help='Fact content'
    )
    add_fact_parser.add_argument(
        '--category', default='general',
        help='Fact category'
    )
    add_fact_parser.add_argument(
        '--source',
        help='Fact source'
    )
    add_fact_parser.add_argument(
        '--confidence', type=float,
        help='Fact confidence (0-1)'
    )
    
    # Get facts
    get_facts_parser = fact_subparsers.add_parser('get', help='Get facts')
    get_facts_parser.add_argument(
        'user_id', help='User ID'
    )
    get_facts_parser.add_argument(
        '--category',
        help='Filter by category'
    )
    
    # Remove fact
    remove_fact_parser = fact_subparsers.add_parser('remove', help='Remove a fact')
    remove_fact_parser.add_argument(
        'user_id', help='User ID'
    )
    remove_fact_parser.add_argument(
        'fact_id', help='Fact ID to remove'
    )
    
    # Global context parsers
    context_parser = subparsers.add_parser('context', help='Global context commands')
    context_subparsers = context_parser.add_subparsers(dest='context_command', help='Context command to execute')
    
    # Set context
    set_context_parser = context_subparsers.add_parser('set', help='Set global context')
    set_context_parser.add_argument(
        'key', help='Context key'
    )
    set_context_parser.add_argument(
        'value', help='Context value (can be JSON string)'
    )
    
    # Get context
    get_context_parser = context_subparsers.add_parser('get', help='Get global context')
    get_context_parser.add_argument(
        'key', help='Context key'
    )
    
    # Delete context
    delete_context_parser = context_subparsers.add_parser('delete', help='Delete global context')
    delete_context_parser.add_argument(
        'key', help='Context key'
    )
    
    return parser


def parse_json_arg(arg_value: Optional[str]) -> Any:
    """
    Parse a JSON string argument.
    
    Args:
        arg_value: JSON string to parse
        
    Returns:
        Parsed JSON value or None
    """
    if not arg_value:
        return None
    
    try:
        return json.loads(arg_value)
    except json.JSONDecodeError:
        # If it's not valid JSON, return as is
        return arg_value


def print_json(data: Any) -> None:
    """
    Print data as formatted JSON.
    
    Args:
        data: Data to print
    """
    print(json.dumps(data, indent=2, sort_keys=True))


def handle_init(args: argparse.Namespace) -> int:
    """
    Handle the init command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    config_override = {}
    
    if args.store_type:
        config_override["MEMORY_STORE_TYPE"] = args.store_type
    
    if args.max_messages:
        config_override["MAX_MESSAGES"] = args.max_messages
    
    if args.data_dir:
        config_override["DATA_DIR"] = args.data_dir
    
    try:
        initialize(config_override=config_override if config_override else None)
        print("Memory management system initialized successfully")
        return 0
    except Exception as e:
        logger.error(f"Error initializing memory management system: {str(e)}")
        return 1


def handle_reset(args: argparse.Namespace) -> int:
    """
    Handle the reset command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    try:
        reset(keep_data=args.keep_data)
        print("Memory management system reset successfully")
        return 0
    except Exception as e:
        logger.error(f"Error resetting memory management system: {str(e)}")
        return 1


def handle_user_command(args: argparse.Namespace) -> int:
    """
    Handle user commands.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    try:
        memory = get_memory_store()
        
        if args.user_command == 'create':
            user = memory.get_or_create_user(args.user_id, args.username)
            print("User created:")
            print_json(user)
            return 0
        
        elif args.user_command == 'get':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            user = memory.get_or_create_user(args.user_id)
            print_json(user)
            return 0
        
        elif args.user_command == 'delete':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            success = memory.remove_user_fact(args.user_id, args.fact_id)
            if success:
                print(f"User {args.user_id} deleted successfully")
                return 0
            else:
                print(f"Failed to delete user {args.user_id}")
                return 1
        
        elif args.user_command == 'update-profile':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            profile_data = {}
            
            if args.name:
                profile_data["name"] = args.name
            
            if args.timezone:
                profile_data["timezone"] = args.timezone
            
            if args.preferences:
                profile_data["preferences"] = parse_json_arg(args.preferences)
            
            updated_profile = memory.update_user_profile(args.user_id, profile_data)
            print("Updated profile:")
            print_json(updated_profile)
            return 0
        
        else:
            print(f"Unknown user command: {args.user_command}")
            return 1
    
    except Exception as e:
        logger.error(f"Error executing user command: {str(e)}")
        return 1


def handle_message_command(args: argparse.Namespace) -> int:
    """
    Handle message commands.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    try:
        memory = get_memory_store()
        
        if args.message_command == 'add':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            metadata = parse_json_arg(args.metadata)
            message = memory.add_message(args.user_id, args.role, args.content, metadata)
            print("Message added:")
            print_json(message)
            return 0
        
        elif args.message_command == 'get':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            messages = memory.get_message_history(args.user_id, args.limit)
            print_json(messages)
            return 0
        
        else:
            print(f"Unknown message command: {args.message_command}")
            return 1
    
    except Exception as e:
        logger.error(f"Error executing message command: {str(e)}")
        return 1


def handle_fact_command(args: argparse.Namespace) -> int:
    """
    Handle fact commands.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    try:
        memory = get_memory_store()
        
        if args.fact_command == 'add':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            fact = memory.add_user_fact(args.user_id, args.fact, args.category, args.source, args.confidence)
            print("Fact added:")
            print_json(fact)
            return 0
        
        elif args.fact_command == 'get':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            facts = memory.get_user_facts(args.user_id, args.category)
            print_json(facts)
            return 0
        
        elif args.fact_command == 'remove':
            if not memory.user_exists(args.user_id):
                print(f"User {args.user_id} does not exist")
                return 1
            
            success = memory.remove_user_fact(args.user_id, args.fact_id)
            if success:
                print(f"Fact {args.fact_id} removed successfully")
                return 0
            else:
                print(f"Failed to remove fact {args.fact_id}")
                return 1
        
        else:
            print(f"Unknown fact command: {args.fact_command}")
            return 1
    
    except Exception as e:
        logger.error(f"Error executing fact command: {str(e)}")
        return 1


def handle_context_command(args: argparse.Namespace) -> int:
    """
    Handle context commands.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code
    """
    try:
        memory = get_memory_store()
        
        if args.context_command == 'set':
            value = parse_json_arg(args.value)
            memory.set_global_context(args.key, value)
            print(f"Global context '{args.key}' set successfully")
            return 0
        
        elif args.context_command == 'get':
            value = memory.get_global_context(args.key)
            if value is None:
                print(f"Global context '{args.key}' not found")
                return 1
            
            print_json(value)
            return 0
        
        elif args.context_command == 'delete':
            success = memory.delete_global_context(args.key)
            if success:
                print(f"Global context '{args.key}' deleted successfully")
                return 0
            else:
                print(f"Failed to delete global context '{args.key}'")
                return 1
        
        else:
            print(f"Unknown context command: {args.context_command}")
            return 1
    
    except Exception as e:
        logger.error(f"Error executing context command: {str(e)}")
        return 1


def main() -> int:
    """
    Main function for CLI.
    
    Returns:
        Exit code
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    if not hasattr(args, 'command'):
        parser.print_help()
        return 1
    
    if args.command == 'init':
        return handle_init(args)
    
    elif args.command == 'reset':
        return handle_reset(args)
    
    elif args.command == 'user':
        if not hasattr(args, 'user_command'):
            print("Error: Missing user command")
            return 1
        return handle_user_command(args)
    
    elif args.command == 'message':
        if not hasattr(args, 'message_command'):
            print("Error: Missing message command")
            return 1
        return handle_message_command(args)
    
    elif args.command == 'fact':
        if not hasattr(args, 'fact_command'):
            print("Error: Missing fact command")
            return 1
        return handle_fact_command(args)
    
    elif args.command == 'context':
        if not hasattr(args, 'context_command'):
            print("Error: Missing context command")
            return 1
        return handle_context_command(args)
    
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 