/*
 * Copyright (C) 2023 Dominik Drexler and Simon Stahlberg
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#ifndef MIMIR_SEARCH_ACTION_HPP_
#define MIMIR_SEARCH_ACTION_HPP_

#include "mimir/formalism/declarations.hpp"
#include "mimir/search/flat_types.hpp"
#include "mimir/search/state.hpp"

#include <ostream>
#include <tuple>

namespace mimir
{
class PDDLFactories;

/**
 * Flatmemory types
 */

struct FlatSimpleEffect
{
    bool is_negated;
    size_t atom_id;

    bool operator==(const FlatSimpleEffect& other) const;
};

using FlatStripsActionPreconditionLayout = flatmemory::Tuple<FlatBitsetLayout<Static>,  //
                                                             FlatBitsetLayout<Static>,
                                                             FlatBitsetLayout<Fluent>,
                                                             FlatBitsetLayout<Fluent>,
                                                             FlatBitsetLayout<Derived>,
                                                             FlatBitsetLayout<Derived>>;
using FlatStripsActionPreconditionBuilder = flatmemory::Builder<FlatStripsActionPreconditionLayout>;
using FlatStripsActionPrecondition = flatmemory::ConstView<FlatStripsActionPreconditionLayout>;

using FlatStripsActionEffectLayout = flatmemory::Tuple<FlatBitsetLayout<Fluent>,   // add effects
                                                       FlatBitsetLayout<Fluent>>;  // delete effects
using FlatStripsActionEffectBuilder = flatmemory::Builder<FlatStripsActionEffectLayout>;
using FlatStripsActionEffect = flatmemory::ConstView<FlatStripsActionEffectLayout>;

using FlatConditionalEffectLayout = flatmemory::Tuple<FlatIndexListLayout,  // Positive static atom indices
                                                      FlatIndexListLayout,  // Negative static atom indices
                                                      FlatIndexListLayout,  // Positive fluent atom indices
                                                      FlatIndexListLayout,  // Negative fluent atom indices
                                                      FlatIndexListLayout,  // Positive derived atom indices
                                                      FlatIndexListLayout,  // Negative derived atom indices
                                                      FlatSimpleEffect>;    // simple add or delete effect
using FlatConditionalEffectBuilder = flatmemory::Builder<FlatConditionalEffectLayout>;
using FlatConditionalEffect = flatmemory::ConstView<FlatConditionalEffectLayout>;

using FlatConditionalEffectsLayout = flatmemory::Vector<FlatConditionalEffectLayout>;  // simple add or delete effect
using FlatConditionalEffectsBuilder = flatmemory::Builder<FlatConditionalEffectsLayout>;
using FlatConditionalEffects = flatmemory::ConstView<FlatConditionalEffectsLayout>;

using FlatSimpleEffectVectorLayout = flatmemory::Vector<FlatSimpleEffect>;
using FlatSimpleEffectVectorBuilder = flatmemory::Builder<FlatSimpleEffectVectorLayout>;
using FlatSimpleEffectVector = flatmemory::ConstView<FlatSimpleEffectVectorLayout>;

using FlatActionLayout = flatmemory::Tuple<GroundActionIndex,  //
                                           GroundActionCost,
                                           Action,
                                           FlatObjectListLayout,
                                           FlatStripsActionPreconditionLayout,
                                           FlatStripsActionEffectLayout,
                                           FlatConditionalEffectsLayout>;
using FlatActionBuilder = flatmemory::Builder<FlatActionLayout>;
using FlatAction = flatmemory::ConstView<FlatActionLayout>;
using FlatActionVector = flatmemory::VariableSizedTypeVector<FlatActionLayout>;

}

template<>
struct std::hash<mimir::FlatAction>
{
    size_t operator()(mimir::FlatAction element) const;
};

template<>
struct std::equal_to<mimir::FlatAction>
{
    bool operator()(mimir::FlatAction lhs, mimir::FlatAction rhs) const;
};

namespace mimir
{

using FlatActionSet = flatmemory::UnorderedSet<FlatActionLayout>;

/**
 * Implementation class
 */

class StripsActionPreconditionBuilderProxy
{
private:
    FlatStripsActionPreconditionBuilder& m_builder;

public:
    explicit StripsActionPreconditionBuilderProxy(FlatStripsActionPreconditionBuilder& builder);

    /* Precondition */

    template<PredicateCategory P>
    FlatBitsetBuilder<P>& get_positive_precondition();

    template<PredicateCategory P>
    FlatBitsetBuilder<P>& get_negative_precondition();
};

class StripsActionPrecondition
{
private:
    FlatStripsActionPrecondition m_view;

public:
    explicit StripsActionPrecondition(FlatStripsActionPrecondition view);

    template<PredicateCategory P>
    FlatBitset<P> get_positive_precondition() const;

    template<PredicateCategory P>
    FlatBitset<P> get_negative_precondition() const;

    template<DynamicPredicateCategory P>
    bool is_applicable(State state) const;

    bool is_dynamically_applicable(State state) const;

    bool is_statically_applicable(FlatBitset<Static> static_positive_atoms) const;

    bool is_applicable(Problem problem, State state) const;

    template<PredicateCategory P>
    bool is_applicable(const FlatBitsetBuilder<P>& atoms) const;

    bool is_applicable(const FlatBitsetBuilder<Fluent>& fluent_state_atoms,
                       const FlatBitsetBuilder<Derived>& derived_state_atoms,
                       const FlatBitsetBuilder<Static>& static_initial_atoms) const;
};

class StripsActionEffectBuilder
{
private:
    FlatStripsActionEffectBuilder& m_builder;

public:
    explicit StripsActionEffectBuilder(FlatStripsActionEffectBuilder& builder);

    FlatBitsetBuilder<Fluent>& get_positive_effects();
    FlatBitsetBuilder<Fluent>& get_negative_effects();
};

class StripsActionEffect
{
private:
    FlatStripsActionEffect m_view;

public:
    explicit StripsActionEffect(FlatStripsActionEffect view);

    FlatBitset<Fluent> get_positive_effects() const;
    FlatBitset<Fluent> get_negative_effects() const;
};

class ConditionalEffectBuilder
{
private:
    FlatConditionalEffectBuilder& m_builder;

public:
    explicit ConditionalEffectBuilder(FlatConditionalEffectBuilder& builder);

    /* Precondition */

    template<PredicateCategory P>
    FlatIndexListBuilder& get_positive_precondition();

    template<PredicateCategory P>
    FlatIndexListBuilder& get_negative_precondition();

    /* Simple effects */

    FlatSimpleEffect& get_simple_effect();
};

class ConditionalEffect
{
private:
    FlatConditionalEffect m_view;

public:
    explicit ConditionalEffect(FlatConditionalEffect view);

    /* Precondition */

    template<PredicateCategory P>
    FlatIndexList get_positive_precondition() const;

    template<PredicateCategory P>
    FlatIndexList get_negative_precondition() const;

    /* Simple effects */
    const FlatSimpleEffect get_simple_effect() const;

    template<DynamicPredicateCategory P>
    bool is_applicable(State state) const;

    bool is_dynamically_applicable(State state) const;

    bool is_statically_applicable(Problem problem) const;

    bool is_applicable(Problem problem, State state) const;
};

class GroundActionBuilder
{
private:
    FlatActionBuilder m_builder;

public:
    FlatActionBuilder& get_flatmemory_builder();
    const FlatActionBuilder& get_flatmemory_builder() const;

    GroundActionIndex& get_index();
    GroundActionCost& get_cost();
    Action& get_action();
    FlatObjectListBuilder& get_objects();

    /* STRIPS part */
    FlatStripsActionPreconditionBuilder& get_strips_precondition();
    FlatStripsActionEffectBuilder& get_strips_effect();
    /* Conditional effects */
    FlatConditionalEffectsBuilder& get_conditional_effects();
};

/**
 * Implementation class
 *
 * Reads the memory layout generated by the search node builder.
 */
class GroundAction
{
private:
    FlatAction m_view;

    static const GroundActionBuilder s_null_ground_action;

public:
    /// @brief Create a view on a DefaultAction.
    explicit GroundAction(FlatAction view);

    static GroundAction get_null_ground_action();

    bool operator==(const GroundAction& other) const;

    GroundActionIndex get_index() const;
    GroundActionCost get_cost() const;
    Action get_action() const;
    FlatObjectList get_objects() const;

    /* STRIPS part */
    FlatStripsActionPrecondition get_strips_precondition() const;
    FlatStripsActionEffect get_strips_effect() const;
    /* Conditional effects */
    FlatConditionalEffects get_conditional_effects() const;

    bool is_dynamically_applicable(State state) const;

    bool is_statically_applicable(FlatBitset<Static> static_positive_atoms) const;

    bool is_applicable(Problem problem, State state) const;
};

}

template<>
struct std::hash<mimir::GroundAction>
{
    size_t operator()(mimir::GroundAction element) const;
};

template<>
struct std::equal_to<mimir::GroundAction>
{
    size_t operator()(mimir::GroundAction lhs, mimir::GroundAction rhs) const;
};

namespace mimir
{

/**
 * Mimir types
 */

using GroundActionList = std::vector<GroundAction>;
using GroundActionSet = std::unordered_set<GroundAction>;

/**
 * Pretty printing
 */

extern std::ostream& operator<<(std::ostream& os, const std::tuple<FlatSimpleEffect, const PDDLFactories&>& data);

extern std::ostream& operator<<(std::ostream& os, const std::tuple<StripsActionPrecondition, const PDDLFactories&>& data);

extern std::ostream& operator<<(std::ostream& os, const std::tuple<StripsActionEffect, const PDDLFactories&>& data);

extern std::ostream& operator<<(std::ostream& os, const std::tuple<ConditionalEffect, const PDDLFactories&>& data);

extern std::ostream& operator<<(std::ostream& os, const std::tuple<GroundAction, const PDDLFactories&>& data);

extern std::ostream& operator<<(std::ostream& os, GroundAction action);

}

#endif
