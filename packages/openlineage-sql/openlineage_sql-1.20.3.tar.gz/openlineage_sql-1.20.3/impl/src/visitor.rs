// Copyright 2018-2024 contributors to the OpenLineage project
// SPDX-License-Identifier: Apache-2.0

use crate::context::Context;
use crate::lineage::*;

use anyhow::{anyhow, Result};
use sqlparser::ast::{
    AlterTableOperation, Expr, FromTable, Function, FunctionArg, FunctionArgExpr, Ident,
    ListAggOnOverflow, Query, Select, SelectItem, SetExpr, Statement, Table, TableFactor,
    WindowSpec, WindowType, With,
};

pub trait Visit {
    fn visit(&self, context: &mut Context) -> Result<()>;
}

impl Visit for With {
    fn visit(&self, context: &mut Context) -> Result<()> {
        for cte in &self.cte_tables {
            context.add_table_alias(
                DbTableMeta::new_default_dialect("".to_string()),
                vec![cte.alias.name.clone()],
            );
            context.push_frame();
            cte.query.visit(context)?;
            let frame = context.pop_frame();
            if let Some(f) = frame {
                let table = DbTableMeta::new(
                    vec![cte.alias.name.clone()],
                    context.dialect(),
                    context.default_schema().clone(),
                );
                context.collect_with_table(f, table);
            }
        }
        Ok(())
    }
}

impl Visit for TableFactor {
    fn visit(&self, context: &mut Context) -> Result<()> {
        match self {
            TableFactor::Table { name, alias, .. } => {
                let table = DbTableMeta::new(
                    name.clone().0,
                    context.dialect(),
                    context.default_schema().clone(),
                );
                if let Some(alias) = alias {
                    context.add_table_alias(table, vec![alias.name.clone()]);
                }
                context.add_input(name.clone().0);
                Ok(())
            }
            TableFactor::Pivot { table, alias, .. } => {
                let ident = get_table_name_from_table_factor(table)?;
                if let Some(pivot_alias) = alias {
                    context.add_table_alias(
                        DbTableMeta::new(
                            ident.clone(),
                            context.dialect(),
                            context.default_schema().clone(),
                        ),
                        vec![pivot_alias.clone().name],
                    );
                }
                context.add_input(ident);
                Ok(())
            }
            TableFactor::Derived {
                lateral: _,
                subquery,
                alias,
            } => {
                context.push_frame();
                subquery.visit(context)?;
                let frame = context.pop_frame().unwrap();

                if let Some(alias) = alias {
                    let table = DbTableMeta::new(
                        vec![alias.clone().name],
                        context.dialect(),
                        context.default_schema().clone(),
                    );
                    context.collect_with_table(frame, table);
                } else {
                    context.collect(frame);
                }

                Ok(())
            }
            TableFactor::TableFunction { .. } => {
                // https://docs.snowflake.com/en/sql-reference/functions-table
                // We can skip them as we don't support extracting lineage from functions
                Ok(())
            }
            _ => Err(anyhow!(
                "TableFactor other than table or subquery not implemented: {self}"
            )),
        }
    }
}

/// Process expression in case where we want to extract lineage (for eg. in subqueries)
/// This means most enum types are untouched, where in other contexts they'd be processed.
impl Visit for Expr {
    fn visit(&self, context: &mut Context) -> Result<()> {
        match self {
            Expr::Subquery(query) | Expr::ArraySubquery(query) => {
                query.visit(context)?;
            }
            Expr::InSubquery {
                expr: _,
                subquery,
                negated: _,
            } => {
                subquery.visit(context)?;
            }
            Expr::BinaryOp { left, op: _, right } => {
                left.visit(context)?;
                right.visit(context)?;
            }
            Expr::UnaryOp { op: _, expr } => {
                expr.visit(context)?;
            }
            Expr::Case {
                operand,
                conditions,
                results,
                else_result,
            } => {
                if let Some(expr) = operand {
                    expr.visit(context)?;
                }

                for condition in conditions {
                    condition.visit(context)?;
                }

                for result in results {
                    result.visit(context)?;
                }

                if let Some(expr) = else_result {
                    expr.visit(context)?;
                }
            }
            Expr::Identifier(id) => {
                let context_set = context.column_context().is_some();
                if context_set {
                    let descendant = context.column_context().as_ref().unwrap().name.clone();
                    context.add_column_ancestors(
                        ColumnMeta::new(descendant, None),
                        vec![ColumnMeta::new(
                            id.value.clone(),
                            context.table_context().clone(),
                        )],
                    );
                }
            }
            Expr::CompoundIdentifier(ids) => {
                let context_set = context.column_context().is_some();
                if context_set {
                    let descendant = context.column_context().as_ref().unwrap().name.clone();
                    let ancestor = ids.last().unwrap().value.clone();
                    let table = DbTableMeta::new(
                        ids.iter().take(ids.len() - 1).cloned().collect(),
                        context.dialect(),
                        context.default_schema().clone(),
                    );
                    context.add_column_ancestors(
                        ColumnMeta::new(descendant, None),
                        vec![ColumnMeta::new(ancestor, Some(table))],
                    );
                }
            }
            Expr::Function(func) => func.visit(context)?,
            Expr::IsFalse(expr)
            | Expr::IsNotFalse(expr)
            | Expr::IsTrue(expr)
            | Expr::IsNotTrue(expr)
            | Expr::IsNull(expr)
            | Expr::IsNotNull(expr)
            | Expr::IsUnknown(expr)
            | Expr::IsNotUnknown(expr) => {
                expr.visit(context)?;
            }
            Expr::AnyOp {
                left,
                compare_op: _,
                right,
            }
            | Expr::AllOp {
                left,
                compare_op: _,
                right,
            } => {
                left.visit(context)?;
                right.visit(context)?;
            }
            Expr::InList { expr, list, .. } => {
                expr.visit(context)?;
                for e in list {
                    e.visit(context)?;
                }
            }
            Expr::Between {
                expr,
                negated: _,
                low,
                high,
            } => {
                expr.visit(context)?;
                low.visit(context)?;
                high.visit(context)?;
            }
            Expr::Like {
                negated: _,
                expr,
                pattern,
                ..
            }
            | Expr::ILike {
                negated: _,
                expr,
                pattern,
                ..
            }
            | Expr::SimilarTo {
                negated: _,
                expr,
                pattern,
                ..
            } => {
                expr.visit(context)?;
                pattern.visit(context)?;
            }
            Expr::Cast { expr, .. } | Expr::TryCast { expr, .. } | Expr::SafeCast { expr, .. } => {
                expr.visit(context)?;
            }
            Expr::AtTimeZone { timestamp, .. } => {
                timestamp.visit(context)?;
            }
            Expr::Extract { field: _, expr } => {
                expr.visit(context)?;
            }
            Expr::Position { expr, r#in } => {
                expr.visit(context)?;
                r#in.visit(context)?;
            }
            Expr::Substring {
                expr,
                substring_from,
                substring_for,
                ..
            } => {
                expr.visit(context)?;
                if let Some(e) = substring_from {
                    e.visit(context)?;
                }
                if let Some(e) = substring_for {
                    e.visit(context)?;
                }
            }
            Expr::Trim {
                expr,
                trim_where: _,
                trim_what,
                ..
            } => {
                expr.visit(context)?;
                if let Some(e) = trim_what {
                    e.visit(context)?;
                }
            }
            Expr::Overlay {
                expr,
                overlay_what,
                overlay_from,
                overlay_for,
            } => {
                expr.visit(context)?;
                overlay_what.visit(context)?;
                overlay_from.visit(context)?;
                if let Some(e) = overlay_for {
                    e.visit(context)?;
                }
            }
            Expr::Collate { expr, .. } => {
                expr.visit(context)?;
            }
            Expr::Nested(expr) => {
                expr.visit(context)?;
            }
            Expr::MapAccess { column, keys } => {
                column.visit(context)?;
                for key in keys {
                    key.visit(context)?;
                }
            }
            Expr::Exists { subquery, .. } => {
                subquery.visit(context)?;
            }
            Expr::GroupingSets(list) | Expr::Cube(list) | Expr::Rollup(list) => {
                for exprs in list {
                    for expr in exprs {
                        expr.visit(context)?;
                    }
                }
            }
            Expr::Tuple(exprs) => {
                for expr in exprs {
                    expr.visit(context)?;
                }
            }
            Expr::ArrayIndex { obj, indexes } => {
                obj.visit(context)?;
                for index in indexes {
                    index.visit(context)?;
                }
            }
            Expr::ListAgg(list) => {
                list.expr.visit(context)?;
                if let Some(e) = &list.separator {
                    e.visit(context)?;
                }
                if let Some(ListAggOnOverflow::Truncate {
                    filler: Some(e), ..
                }) = &list.on_overflow
                {
                    e.visit(context)?;
                }
                for order_by in &list.within_group {
                    order_by.expr.visit(context)?;
                }
            }
            Expr::Array(array) => {
                for e in &array.elem {
                    e.visit(context)?;
                }
            }
            Expr::JsonAccess {
                left,
                operator: _,
                right,
            } => {
                left.visit(context)?;
                right.visit(context)?;
            }
            Expr::CompositeAccess { expr, .. } => {
                expr.visit(context)?;
            }
            Expr::IsDistinctFrom(left, right) | Expr::IsNotDistinctFrom(left, right) => {
                left.visit(context)?;
                right.visit(context)?;
            }
            Expr::InUnnest {
                expr, array_expr, ..
            } => {
                expr.visit(context)?;
                array_expr.visit(context)?;
            }
            _ => {}
        }
        Ok(())
    }
}

impl Visit for Function {
    fn visit(&self, context: &mut Context) -> Result<()> {
        for arg in &self.args {
            arg.visit(context)?;
        }

        if let Some(spec) = &self.over {
            spec.visit(context)?;
        }

        Ok(())
    }
}

impl Visit for FunctionArg {
    fn visit(&self, context: &mut Context) -> Result<()> {
        match self {
            FunctionArg::Named {
                name: _,
                arg,
                operator: _,
            } => arg.visit(context),
            FunctionArg::Unnamed(arg) => arg.visit(context),
        }
    }
}

impl Visit for FunctionArgExpr {
    fn visit(&self, context: &mut Context) -> Result<()> {
        match self {
            FunctionArgExpr::Expr(expr) => expr.visit(context),
            _ => Ok(()),
        }
    }
}

impl Visit for WindowType {
    fn visit(&self, context: &mut Context) -> Result<()> {
        match self {
            WindowType::WindowSpec(spec) => spec.visit(context),
            WindowType::NamedWindow(..) => Ok(()),
        }
    }
}
impl Visit for WindowSpec {
    fn visit(&self, context: &mut Context) -> Result<()> {
        for expr in &self.partition_by {
            expr.visit(context)?;
        }

        for order in &self.order_by {
            order.expr.visit(context)?;
        }

        Ok(())
    }
}

impl Visit for Select {
    fn visit(&self, context: &mut Context) -> Result<()> {
        // If we're selecting from a single table, that table becomes the default
        if self.from.len() == 1 {
            let t = self.from.first().unwrap();
            if let TableFactor::Table { name, alias, .. } = &t.relation {
                let table = DbTableMeta::new(
                    name.clone().0,
                    context.dialect(),
                    context.default_schema().clone(),
                );
                if let Some(alias) = alias {
                    context.add_table_alias(table.clone(), vec![alias.clone().name]);
                }
                context.set_table_context(Some(table));
            }
        }

        context.push_frame();

        for table in &self.from {
            context.push_frame();
            table.relation.visit(context)?;
            let frame = context.pop_frame().unwrap();
            context.collect_aliases(&frame);
            context.collect(frame);

            for join in &table.joins {
                context.push_frame();
                join.relation.visit(context)?;
                let frame = context.pop_frame().unwrap();
                context.collect_aliases(&frame);
                context.collect(frame);
            }
        }

        let tables_frame = context.pop_frame().unwrap();
        context.collect_aliases(&tables_frame);

        for projection in &self.projection {
            match projection {
                SelectItem::UnnamedExpr(expr) => {
                    match expr {
                        Expr::Identifier(id) => context
                            .set_column_context(Some(ColumnMeta::new(id.value.clone(), None))),
                        Expr::CompoundIdentifier(ids) => context.set_column_context(Some(
                            ColumnMeta::new(ids.last().unwrap().value.clone(), None),
                        )),
                        _ => context.set_unnamed_column_context(),
                    };
                    expr.visit(context)?;
                }
                SelectItem::ExprWithAlias { expr, alias } => {
                    context.set_column_context(Some(ColumnMeta::new(alias.value.clone(), None)));
                    expr.visit(context)?;
                }
                _ => {}
            }
        }

        context.set_column_context(None);

        if let Some(into) = &self.into {
            context.add_output(into.name.clone().0)
        }

        context.set_table_context(None);

        context.coalesce(tables_frame);

        Ok(())
    }
}

impl Visit for SetExpr {
    fn visit(&self, context: &mut Context) -> Result<()> {
        match self {
            SetExpr::Select(select) => select.visit(context),
            SetExpr::Values(_) => Ok(()),
            SetExpr::Insert(stmt) => stmt.visit(context),
            SetExpr::Query(q) => q.visit(context),
            SetExpr::SetOperation {
                op: _,
                set_quantifier: _,
                left,
                right,
            } => {
                left.visit(context)?;
                right.visit(context)
            }
            SetExpr::Table(table) => table.visit(context),
            SetExpr::Update(stmt) => stmt.visit(context),
        }
    }
}

impl Visit for Query {
    fn visit(&self, context: &mut Context) -> Result<()> {
        context.push_frame();
        match &self.with {
            Some(with) => with.visit(context)?,
            None => (),
        }
        let with_frame = context.pop_frame().unwrap();

        context.collect_aliases(&with_frame);

        context.push_frame();
        self.body.visit(context)?;
        let frame = context.pop_frame().unwrap();
        context.collect(frame);

        // Resolve CTEs
        context.coalesce(with_frame);

        Ok(())
    }
}

impl Visit for Statement {
    fn visit(&self, context: &mut Context) -> Result<()> {
        context.push_frame();
        match self {
            Statement::Query(query) => query.visit(context)?,
            Statement::Insert {
                table_name, source, ..
            } => {
                if let Some(src) = source {
                    src.visit(context)?;
                }
                context.add_output(table_name.clone().0);
            }
            Statement::Merge { table, source, .. } => {
                let table_name = get_table_name_from_table_factor(table)?;
                context.add_output(table_name);
                source.visit(context)?;
            }
            Statement::CreateTable {
                name,
                query,
                like,
                clone,
                ..
            } => {
                if let Some(query) = query {
                    query.visit(context)?;
                }
                if let Some(like_table) = like {
                    context.add_input(like_table.clone().0);
                }
                if let Some(clone) = clone {
                    context.add_input(clone.clone().0);
                }

                context.add_output(name.clone().0);
            }
            Statement::CreateView { name, query, .. } => {
                query.visit(context)?;
                context.add_output(name.clone().0);
            }
            Statement::CreateStage {
                name, stage_params, ..
            } => {
                if stage_params.url.as_ref().is_some() {
                    context.add_non_table_input(
                        vec![Ident::new(stage_params.url.as_ref().unwrap().to_string())],
                        true,
                        true,
                    );
                }
                context.add_non_table_output(name.clone().0, false, true);
            }
            Statement::Update {
                table,
                assignments: _,
                from,
                selection,
                ..
            } => {
                let name = get_table_name_from_table_factor(&table.relation)?;
                context.add_output(name);

                if let Some(src) = from {
                    src.relation.visit(context)?;
                    for join in &src.joins {
                        join.relation.visit(context)?;
                    }
                }
                if let Some(expr) = selection {
                    expr.visit(context)?;
                }
            }
            Statement::AlterTable {
                name,
                if_exists: _,
                only: _,
                operations,
                location: _,
            } => {
                for operation in operations {
                    match operation {
                        AlterTableOperation::SwapWith { table_name } => {
                            // both table names are inputs and outputs of the swap operation
                            context.add_input(table_name.clone().0);
                            context.add_input(name.clone().0);

                            context.add_output(table_name.clone().0);
                            context.add_output(name.clone().0);
                        }
                        AlterTableOperation::RenameTable { table_name } => {
                            context.add_input(name.clone().0);
                            context.add_output(table_name.clone().0);
                        }
                        _ => context.add_output(name.clone().0),
                    }
                }
            }
            Statement::Delete {
                tables: _,
                from,
                using,
                selection,
                ..
            } => {
                match from {
                    FromTable::WithFromKeyword(tables) | FromTable::WithoutKeyword(tables) => {
                        for table in tables {
                            let output = get_table_name_from_table_factor(&table.relation)?;
                            context.add_output(output);
                            for join in &table.joins {
                                let join_output = get_table_name_from_table_factor(&join.relation)?;
                                context.add_output(join_output);
                            }
                        }
                    }
                }

                if let Some(using) = using {
                    for table in using {
                        table.relation.visit(context)?;
                        for join in &table.joins {
                            join.relation.visit(context)?;
                        }
                    }
                }

                if let Some(expr) = selection {
                    expr.visit(context)?;
                }
            }
            Statement::Truncate { table_name, .. } => context.add_output(table_name.clone().0),
            Statement::Drop { names, .. } => {
                for name in names {
                    context.add_output(name.clone().0)
                }
            }
            Statement::CopyIntoSnowflake {
                into, from_stage, ..
            } => {
                context.add_output(into.clone().0);
                if from_stage.to_string().contains("gcs://")
                    || from_stage.to_string().contains("s3://")
                    || from_stage.to_string().contains("azure://")
                {
                    context.add_non_table_input(
                        vec![Ident::new(from_stage.to_string().replace(['\"', '\''], ""))], // just unquoted location URL with,
                        true,
                        true,
                    );
                } else {
                    // Stage
                    context.add_non_table_input(from_stage.clone().0, true, true);
                };
            }
            _ => {}
        }

        let frame = context.pop_frame().unwrap();
        context.collect(frame);

        Ok(())
    }
}

impl Visit for Table {
    fn visit(&self, context: &mut Context) -> Result<()> {
        if let Some(name) = &self.table_name {
            context.add_input(vec![Ident::new(name.to_string())])
        }
        Ok(())
    }
}

// --- Utils ---

fn get_table_name_from_table_factor(table: &TableFactor) -> Result<Vec<Ident>> {
    if let TableFactor::Table { name, .. } = table {
        Ok(name.clone().0)
    } else {
        Err(anyhow!(
            "Name can be got only from simple table, got {table}"
        ))
    }
}
