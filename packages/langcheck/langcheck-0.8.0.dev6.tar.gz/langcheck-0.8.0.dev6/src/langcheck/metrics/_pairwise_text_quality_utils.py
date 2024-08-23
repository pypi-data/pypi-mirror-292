from __future__ import annotations


def generate_pairwise_comparison_prompt_params(
    generated_outputs_1: list[str],
    generated_outputs_2: list[str],
    prompts: list[str],
    sources_1: list[str] | None,
    sources_2: list[str] | None,
    reference_outputs: list[str] | None,
) -> list[dict[str, str | None]]:
    """Generate a list of parameters that can be used for the jinja templates
    of the pairwise comparison metrics.

    Args:
        generated_outputs_1: Model 1's generated output(s) to evaluate
        generated_outputs_2: Model 2's generated output(s) to evaluate
        prompts: The prompts used to generate the output(s).
        sources_1: (Optional) the source(s) of Model 1's generated output(s)
        sources_2: (Optional) the source(s) of Model 2's generated output(s)
        reference_outputs: (Optional) the reference output(s)

    Returns:
        A list of dictionaries containing the parameters for the jinja
        templates the formats are as follows:
        [
            {
                'src': SOURCE,
                'ref_output': REFERENCE_OUTPUT,
                'user_query': PROMPT,
                'gen_output_1': GENERATED_OUTPUT_1,
                'gen_output_2': GENERATED_OUTPUT_2
            },
            ...
        ]
    """
    # Combine sources_1 and sources_2 into a single list if both are
    # provided.
    if sources_1 is not None and sources_2 is not None:
        sources = []
        for source_1, source_2 in zip(sources_1, sources_2):
            if source_1 is None:
                sources.append(source_2)
            elif source_2 is None:
                sources.append(source_1)
            else:
                sources.append(source_1 + "\n" + source_2)
    else:
        sources = sources_1 if sources_1 is not None else sources_2

    if sources is None:
        sources_list = [None] * len(prompts)
    else:
        sources_list = sources

    if reference_outputs is None:
        reference_outputs_list = [None] * len(prompts)
    else:
        reference_outputs_list = reference_outputs

    return [
        {
            "src": src,
            "ref_output": ref_output,
            "user_query": prompt,
            "gen_output_1": gen_output_1,
            "gen_output_2": gen_output_2,
        }
        for src, ref_output, prompt, gen_output_1, gen_output_2 in zip(
            sources_list,
            reference_outputs_list,
            prompts,
            generated_outputs_1,
            generated_outputs_2,
        )
    ]


def enforce_pairwise_comparison_consistency(
    original_scores: list[float | None],
    original_explanations: list[str | None],
    swapped_scores: list[float | None],
    swapped_explanations: list[str | None],
    score_map: dict[str, float],
) -> tuple[list[float | None], list[str | None]]:
    """Enforce consistency in pairwise comparison scores.

    Args:
        original_scores: The scores for the original order of the models
        original_explanations: The explanations for the original order of the
            models
        swapped_scores: The scores for the swapped order of the models
        swapped_explanations: The explanations for the swapped order of the
            models
        score_map: The mapping from the assessment results to the scores (e.g.
            {'Response A': 0.0, 'Response B': 1.0, 'Tie': 0.5})
    """
    # Get the sorted list of available scores
    sorted_available_scores = list(score_map.values())
    sorted_available_scores.sort()

    # Iterate through the scores and explanations to check for consistency.
    # If a score is not consistent, set it to None, and merge the two
    # explanations to show the inconsistency.
    scores = original_scores.copy()
    explanations = original_explanations.copy()
    for i in range(len(scores)):
        if scores[i] is None or swapped_scores[i] is None:
            # If either score is None, we cannot determine consistency, so
            # we set the score and explanation to None
            scores[i] = None
            explanations[i] = None
            continue

        # A score is consistent if the score's index in the
        # sorted_available_scores list is the inverse of the swapped score's
        # index. For example, if the score_map is
        # {'Response A': 0.0, 'Response B': 1.0, 'Tie': 0.5}, and the score is
        # 0.0, the swapped score should be 1.0.
        if (
            sorted_available_scores.index(scores[i])  # type: ignore
            + sorted_available_scores.index(swapped_scores[i])  # type: ignore
            != len(sorted_available_scores) - 1
        ):
            scores[i] = None
            explanations[i] = (
                f"Original assessment: {explanations[i]}\nSwapped assessment: {swapped_explanations[i]}"
            )
    return scores, explanations
