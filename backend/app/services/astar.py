
import heapq
import itertools
import math

import networkx as nx


def h(G, node, target):
    """Haversine straight-line distance in meters."""
    lat1 = math.radians(G.nodes[node]["y"])
    lon1 = math.radians(G.nodes[node]["x"])
    lat2 = math.radians(G.nodes[target]["y"])
    lon2 = math.radians(G.nodes[target]["x"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    a = max(0.0, min(1.0, a))

    return (
        2 * 6_371_000
        * math.asin(math.sqrt(a))
    )


def get_edge_length(G, u, v):
    """Return the minimum weight among parallel edges."""
    edge_data = G.get_edge_data(u, v)

    if not edge_data:
        return None

    # Matches NetworkX's default weight of 1 for an
    # edge whose requested weight attribute is missing.
    weights = [
        data.get("length", 1)
        for data in edge_data.values()
    ]

    if any(weight < 0 for weight in weights):
        raise ValueError("A* requires nonnegative edge weights.")

    return min(weights)


def bidirectional_astar(G, source, target):
    """
    Return (distance_m, route_nodes), compatible with
    nx.bidirectional_dijkstra(..., weight="length").
    """
    if source not in G:
        raise nx.NodeNotFound(f"Source node {source} is not in G")

    if target not in G:
        raise nx.NodeNotFound(f"Target node {target} is not in G")

    if source == target:
        return 0.0, [source]

    # Balanced potential for bidirectional A*.
    potential_cache = {}

    def potential(node):
        if node not in potential_cache:
            potential_cache[node] = (
                h(G, node, target) - h(G, source, node)
            ) / 2.0

        return potential_cache[node]

    # Priority queues store (priority, tie_breaker, node).
    counter = itertools.count()

    forward_queue = [
        (potential(source), next(counter), source)
    ]
    backward_queue = [
        (-potential(target), next(counter), target)
    ]

    forward_dist = {source: 0.0}
    backward_dist = {target: 0.0}

    # Forward parent points toward the source.
    forward_parent = {source: None}

    # Backward parent points toward the target.
    backward_parent = {target: None}

    forward_settled = set()
    backward_settled = set()

    best_distance = math.inf
    meeting_node = None

    def update_meeting(node):
        nonlocal best_distance, meeting_node

        if (
            node in forward_dist
            and node in backward_dist
        ):
            candidate = (
                forward_dist[node] + backward_dist[node]
            )

            if candidate < best_distance:
                best_distance = candidate
                meeting_node = node

    def clean_queue(queue, distances, settled, sign):
        """Discard outdated or already settled entries."""
        while queue:
            priority, _, node = queue[0]

            expected = distances[node] + sign * potential(node)

            if node in settled or priority > expected + 1e-9:
                heapq.heappop(queue)
                continue

            return priority

        return math.inf

    def pop_valid(queue, distances, settled, sign):
        clean_queue(queue, distances, settled, sign)

        if not queue:
            return None

        _, _, node = heapq.heappop(queue)
        return node

    while forward_queue and backward_queue:
        min_forward = clean_queue(
            forward_queue,
            forward_dist,
            forward_settled,
            +1,
        )

        min_backward = clean_queue(
            backward_queue,
            backward_dist,
            backward_settled,
            -1,
        )

        if math.isinf(min_forward) or math.isinf(min_backward):
            break

        # The balanced-potential stopping condition.
        if (
            meeting_node is not None
            and min_forward + min_backward
            >= best_distance - 1e-9
        ):
            break

        if min_forward <= min_backward:
            # Expand forward: follow original outgoing edges.
            current = pop_valid(
                forward_queue,
                forward_dist,
                forward_settled,
                +1,
            )

            if current is None:
                break

            forward_settled.add(current)
            update_meeting(current)

            for neighbor in G.successors(current):
                edge_length = get_edge_length(
                    G, current, neighbor
                )

                if edge_length is None:
                    continue

                candidate = (
                    forward_dist[current] + edge_length
                )

                if candidate < forward_dist.get(
                    neighbor, math.inf
                ):
                    if neighbor in forward_settled:
                        continue

                    forward_dist[neighbor] = candidate
                    forward_parent[neighbor] = current

                    priority = candidate + potential(neighbor)

                    heapq.heappush(
                        forward_queue,
                        (priority, next(counter), neighbor),
                    )

                    update_meeting(neighbor)

        else:
            # Expand backward: follow original incoming edges.
            current = pop_valid(
                backward_queue,
                backward_dist,
                backward_settled,
                -1,
            )

            if current is None:
                break

            backward_settled.add(current)
            update_meeting(current)

            for neighbor in G.predecessors(current):
                # The original directed edge is neighbor -> current.
                edge_length = get_edge_length(
                    G, neighbor, current
                )

                if edge_length is None:
                    continue

                candidate = (
                    backward_dist[current] + edge_length
                )

                if candidate < backward_dist.get(
                    neighbor, math.inf
                ):
                    if neighbor in backward_settled:
                        continue

                    backward_dist[neighbor] = candidate
                    backward_parent[neighbor] = current

                    priority = candidate - potential(neighbor)

                    heapq.heappush(
                        backward_queue,
                        (priority, next(counter), neighbor),
                    )

                    update_meeting(neighbor)

    if meeting_node is None:
        raise nx.NetworkXNoPath(
            f"No path between {source} and {target}"
        )

    # Reconstruct source -> meeting node.
    left_route = []
    node = meeting_node

    while node is not None:
        left_route.append(node)
        node = forward_parent[node]

    left_route.reverse()

    # Reconstruct meeting node -> target.
    right_route = []
    node = backward_parent[meeting_node]

    while node is not None:
        right_route.append(node)
        node = backward_parent[node]

    route_nodes = left_route + right_route

    distance_m = (
        forward_dist[meeting_node]
        + backward_dist[meeting_node]
    )

    return distance_m, route_nodes
