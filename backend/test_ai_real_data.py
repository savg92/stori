"""Test script to check database data and AI service."""

import asyncio
from datetime import date, timedelta
from services.supabase_service import get_supabase_client
from src.modules.ai.service import AIService
from src.modules.ai.repository import AIRepository
from src.modules.ai.schemas import AdviceRequest, AdviceType

async def check_database_data():
    """Check what data is in the database."""
    try:
        # Get Supabase client with service role key to bypass RLS
        from supabase import create_client
        from config.settings import Settings
        
        settings = Settings()
        supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Use service role key
        )
        
        # Check total transaction count
        result = supabase_client.table('transactions').select('*').execute()
        print(f'Total transactions in database: {len(result.data)}')
        
        # Get a sample of recent transactions
        recent = supabase_client.table('transactions').select('*').order('date', desc=True).limit(10).execute()
        print(f'\nRecent transactions:')
        for txn in recent.data:
            print(f'  {txn["date"]} | {txn["user_id"]} | {txn["type"]} | ${txn["amount"]} | {txn["category"]}')
        
        # Check user distribution
        users = supabase_client.table('transactions').select('user_id').execute()
        user_counts = {}
        for txn in users.data:
            user_id = txn['user_id']
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        print(f'\nTransactions per user:')
        for user_id, count in sorted(user_counts.items()):
            print(f'  {user_id}: {count} transactions')
            
        # Check date range
        date_range = supabase_client.table('transactions').select('date').order('date', desc=False).limit(1).execute()
        oldest_date = date_range.data[0]['date'] if date_range.data else None
        print(f'\nOldest transaction date: {oldest_date}')
        
        date_range = supabase_client.table('transactions').select('date').order('date', desc=True).limit(1).execute()
        newest_date = date_range.data[0]['date'] if date_range.data else None
        print(f'Newest transaction date: {newest_date}')
        
        return supabase_client, user_counts
        
    except Exception as e:
        print(f'❌ Error checking database: {e}')
        import traceback
        traceback.print_exc()
        return None, {}

async def test_ai_with_extended_period(supabase_client, user_counts):
    """Test AI service with a longer time period."""
    try:
        # Create repository and service with service role client
        repo = AIRepository(supabase_client)
        service = AIService(repo)
        
        # Find user with most transactions
        best_user = max(user_counts.items(), key=lambda x: x[1])
        user_id, txn_count = best_user
        
        print(f'\n🧮 Testing AI service with {user_id} ({txn_count} transactions):')
        
        # Test with a longer time period to catch older data
        request = AdviceRequest(
            advice_type=AdviceType.SPENDING_INSIGHTS,
            time_period_days=365,  # 1 year to catch all data
            context='Show me my spending patterns'
        )
        
        result = await service.get_financial_advice(user_id, request)
        print(f'✅ Summary: {result.summary}')
        print(f'📊 Insights: {len(result.insights)}')
        print(f'🎯 Recommendations: {len(result.recommendations)}')
        
        if result.insights:
            for i, insight in enumerate(result.insights):
                print(f'  💡 Insight {i+1}: {insight.title}')
                print(f'     📝 {insight.description}')
        
        if result.recommendations:
            print(f'\n🔧 Recommendations:')
            for i, rec in enumerate(result.recommendations[:3]):
                print(f'  {i+1}. {rec}')
                
        print(f'\n📈 Data Analysis:')
        for key, value in result.data_analysis.items():
            print(f'  {key}: {value}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error testing AI: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🔍 Checking database data...")
    supabase_client, user_counts = await check_database_data()
    
    if supabase_client and user_counts:
        print("\n🤖 Testing AI service with real data...")
        success = await test_ai_with_extended_period(supabase_client, user_counts)
        
        if success:
            print("\n✅ AI service is working with real data!")
        else:
            print("\n❌ AI service test failed")
    else:
        print("\n❌ Could not connect to database")

if __name__ == '__main__':
    asyncio.run(main())