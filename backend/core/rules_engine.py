import re
import logging
from typing import List, Any
from sqlalchemy.orm import Session
from sqlmodel import select
from ..models.rules import Rule, RuleGroup, RuleTrigger, RuleAction, TriggerType, ActionType
from ..models import Transaction, Category

logger = logging.getLogger("rules_engine")

class RulesEngine:
    """
    Automatic rule processor inspired by Firefly III.
    Matches transactions against criteria and applies actions.
    """

    def __init__(self, db: Session):
        self.db = db

    def apply_rules(self, transaction: Transaction):
        """Processes a transaction through all active rules."""
        groups = self.db.exec(
            select(RuleGroup).where(RuleGroup.is_active == True).order_by(RuleGroup.order)
        ).all()

        modified = False
        for group in groups:
            for rule in group.rules:
                if not rule.is_active:
                    continue
                
                if self._check_rule(rule, transaction):
                    logger.info(f"Applying rule '{rule.name}' to transaction {transaction.id}")
                    self._apply_actions(rule, transaction)
                    modified = True
                    
                    if rule.stop_processing:
                        return modified
        
        return modified

    def _check_rule(self, rule: Rule, tx: Transaction) -> bool:
        """Evaluate triggers based on trigger_mode (ALL/ANY)."""
        results = []
        for trigger in rule.triggers:
            res = self._eval_trigger(trigger, tx)
            results.append(res)
            
        if not results:
            return False
            
        if rule.trigger_mode == "ALL":
            return all(results)
        else: # ANY
            return any(results)

    def _eval_trigger(self, trigger: RuleTrigger, tx: Transaction) -> bool:
        """Individual trigger evaluation logic."""
        if trigger.type == TriggerType.DESCRIPTION_CONTAINS:
            return trigger.value.lower() in (tx.description or "").lower()
        
        elif trigger.type == TriggerType.AMOUNT_IS:
            return tx.monto_transaccion == float(trigger.value) # Need to handle Decimal/float carefully
            
        # Add more trigger types here (regex, category check, etc.)
        return False

    def _apply_actions(self, rule: Rule, tx: Transaction):
        """Executes actions attached to a rule."""
        for action in rule.actions:
            if action.type == ActionType.SET_CATEGORY:
                tx.id_categoria = int(action.value)
            elif action.type == ActionType.SET_PAYEE:
                tx.payee_id = int(action.value)
            # Add more action types
        
        self.db.add(tx)
        self.db.flush()
