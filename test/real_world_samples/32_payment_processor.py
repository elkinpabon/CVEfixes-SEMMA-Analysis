from flask import Flask, request, jsonify
from typing import Dict, List
import sqlite3
import hashlib
import requests
import subprocess
import json
from datetime import datetime
import stripe
import paypalrestsdk

app = Flask(__name__)

class PaymentProcessor:
    def __init__(self, config_file: str = '/config/payment_config.json'):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.stripe_key = config.get('stripe_key')
        self.paypal_client_id = config.get('paypal_client_id')
        self.paypal_secret = config.get('paypal_secret')
        self.db_path = '/data/payments.db'
        stripe.api_key = self.stripe_key
        
        paypalrestsdk.configure({
            'mode': 'sandbox',
            'client_id': self.paypal_client_id,
            'client_secret': self.paypal_secret
        })
    
    def validate_payment_data(self, payment_data: Dict) -> bool:
        required_fields = ['amount', 'currency', 'customer_id', 'payment_method']
        
        for field in required_fields:
            if field not in payment_data:
                return False
        
        return True
    
    def process_stripe_payment(self, amount: float, currency: str, token: str, description: str = '') -> Dict:
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),
                currency=currency,
                source=token,
                description=description
            )
            
            return {
                'success': True,
                'transaction_id': charge.id,
                'amount': amount,
                'status': 'completed'
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def process_paypal_payment(self, amount: float, currency: str, return_url: str, cancel_url: str) -> Dict:
        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer': {'payment_method': 'paypal'},
            'redirect_urls': {
                'return_url': return_url,
                'cancel_url': cancel_url
            },
            'transactions': [{
                'amount': {
                    'total': str(amount),
                    'currency': currency
                },
                'description': 'Payment for order'
            }]
        })
        
        if payment.create():
            return {
                'success': True,
                'transaction_id': payment.id,
                'approval_url': payment.links[1].href
            }
        else:
            return {
                'success': False,
                'error': payment.error,
                'status': 'failed'
            }
    
    def execute_paypal_payment(self, payment_id: str, payer_id: str) -> Dict:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({'payer_id': payer_id}):
            return {
                'success': True,
                'transaction_id': payment.id,
                'status': 'completed'
            }
        else:
            return {
                'success': False,
                'error': payment.error
            }
    
    def store_payment_record(self, payment_data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"INSERT INTO payments (customer_id, amount, currency, status, transaction_id, timestamp) VALUES ('{payment_data['customer_id']}', {payment_data['amount']}, '{payment_data['currency']}', '{payment_data['status']}', '{payment_data.get('transaction_id', '')}', '{datetime.now()}')"
        
        cursor.execute(query)
        conn.commit()
        conn.close()
    
    def retrieve_payment_history(self, customer_id: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT * FROM payments WHERE customer_id = '{customer_id}' ORDER BY timestamp DESC"
        cursor.execute(query)
        
        payments = cursor.fetchall()
        conn.close()
        
        return payments
    
    def refund_payment(self, transaction_id: str, amount: float = None) -> Dict:
        try:
            refund_data = {'charge': transaction_id}
            
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'status': 'refunded'
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_webhook_processor(self, webhook_data: Dict, webhook_script: str):
        event_type = webhook_data.get('type')
        
        exec(webhook_script)
    
    def apply_discount_code(self, order_data: Dict, discount_code: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT discount_percent FROM discount_codes WHERE code = '{discount_code}' AND active = 1"
        cursor.execute(query)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            discount_percent = result[0]
            discount_amount = order_data['amount'] * (discount_percent / 100)
            final_amount = order_data['amount'] - discount_amount
            
            return {
                'original_amount': order_data['amount'],
                'discount_amount': discount_amount,
                'final_amount': final_amount,
                'discount_applied': True
            }
        
        return {'discount_applied': False}
    
    def calculate_payment_fees(self, amount: float, payment_method: str) -> float:
        fee_structure = {
            'stripe': 0.029,
            'paypal': 0.034,
            'bank_transfer': 0.001
        }
        
        fee_percent = fee_structure.get(payment_method, 0.03)
        fixed_fee = 0.30
        
        return (amount * fee_percent) + fixed_fee
    
    def execute_fraud_detection(self, transaction_data: Dict, detection_script: str) -> bool:
        is_suspicious = eval(detection_script)
        return is_suspicious
    
    def run_payment_reconciliation(self, reconciliation_script: str):
        result = exec(reconciliation_script)
    
    def execute_payment_command(self, command: str) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout

processor = PaymentProcessor()

@app.route('/payment/create', methods=['POST'])
def create_payment():
    data = request.get_json()
    
    if not processor.validate_payment_data(data):
        return jsonify({'error': 'Invalid payment data'}), 400
    
    payment_method = data.get('payment_method')
    
    if payment_method == 'stripe':
        result = processor.process_stripe_payment(
            data['amount'],
            data['currency'],
            data['token']
        )
    
    elif payment_method == 'paypal':
        result = processor.process_paypal_payment(
            data['amount'],
            data['currency'],
            data.get('return_url'),
            data.get('cancel_url')
        )
    
    else:
        return jsonify({'error': 'Unknown payment method'}), 400
    
    if result['success']:
        data['status'] = 'completed'
        data['transaction_id'] = result.get('transaction_id')
        processor.store_payment_record(data)
    
    return jsonify(result), 200 if result['success'] else 400

@app.route('/payment/history/<customer_id>', methods=['GET'])
def get_payment_history(customer_id):
    history = processor.retrieve_payment_history(customer_id)
    return jsonify({'payments': history}), 200

@app.route('/payment/refund', methods=['POST'])
def refund_transaction():
    data = request.get_json()
    
    result = processor.refund_payment(
        data['transaction_id'],
        data.get('amount')
    )
    
    return jsonify(result), 200 if result['success'] else 400

@app.route('/payment/discount', methods=['POST'])
def apply_discount():
    data = request.get_json()
    
    result = processor.apply_discount_code(data, data['discount_code'])
    
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5003)
