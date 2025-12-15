"""Updated networth calculations

Revision ID: dda73d7777c1
Revises: 164b59ec1701
Create Date: 2025-12-13 23:16:51.566884

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dda73d7777c1"
down_revision: Union[str, Sequence[str], None] = "164b59ec1701"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("DROP VIEW IF EXISTS total_summary CASCADE")

    op.execute(
        """
        CREATE OR REPLACE VIEW total_summary AS
        WITH transaction_summary AS (
            SELECT
                u.id AS user_id,
                EXTRACT(MONTH FROM t.date) AS month,
                EXTRACT(YEAR FROM t.date) AS year,
                ROUND(SUM(
                    CASE WHEN t.transaction_type = 'income'
                    THEN (t.amount * (udc.exchange_rate / uc.exchange_rate))
                    ELSE 0 END
                )) AS total_income,
                ROUND(SUM(
                    CASE WHEN t.transaction_type = 'expense'
                    THEN (t.amount * (udc.exchange_rate / uc.exchange_rate))
                    ELSE 0 END
                )) AS total_expense,
                ROUND(SUM(
                    CASE 
                        WHEN t.transaction_type = 'income'
                        THEN (t.amount * (udc.exchange_rate / uc.exchange_rate))
                        WHEN t.transaction_type = 'expense'
                        THEN -(t.amount * (udc.exchange_rate / uc.exchange_rate))
                        ELSE 0
                    END
                )) AS net_total
            FROM users u
            JOIN users_currencies udc 
                ON udc.user_id = u.id AND udc.is_default = TRUE
            LEFT JOIN transactions t 
                ON t.user_id = u.id
            LEFT JOIN users_currencies uc 
                ON uc.id = t.user_currency_id
            GROUP BY 
                u.id, udc.exchange_rate,
                EXTRACT(MONTH FROM t.date), 
                EXTRACT(YEAR FROM t.date)
        ),
        account_summary AS (
            SELECT
                a.user_id,
                ROUND(SUM(
                    CASE WHEN a.is_deleted = FALSE
                    THEN (a.amount * (udc.exchange_rate / auc.exchange_rate))
                    ELSE 0 END
                )) AS total_balance
            FROM accounts a
            JOIN users u 
                ON a.user_id = u.id
            JOIN users_currencies udc 
                ON udc.user_id = u.id AND udc.is_default = TRUE
            LEFT JOIN users_currencies auc 
                ON auc.id = a.user_currency_id
            GROUP BY 
                a.user_id, udc.exchange_rate
        )
        SELECT
            u.id AS user_id,
            udc.id AS default_user_currency_id,
            dc.code AS default_currency_code,
            ts.month,
            ts.year,
            COALESCE(ts.total_income, 0) AS total_income,
            COALESCE(ts.total_expense, 0) AS total_expense,
            COALESCE(ts.net_total, 0) AS net_total,
            COALESCE(asum.total_balance, 0) AS total_balance,
            ROUND(COALESCE(asum.total_balance, 0) + COALESCE(ts.net_total, 0)) AS total_cash_at_hand
        FROM users u
        JOIN users_currencies udc 
            ON udc.user_id = u.id AND udc.is_default = TRUE
        JOIN currencies dc 
            ON dc.id = udc.currency_id
        LEFT JOIN transaction_summary ts 
            ON ts.user_id = u.id
        LEFT JOIN account_summary asum 
            ON asum.user_id = u.id
        ORDER BY ts.year, ts.month;
        """
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS total_summary CASCADE")
