/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace sdy {
class ShardableRegionOpInterface;
namespace detail {
struct ShardableRegionOpInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    mlir::sdy::TensorShardingAttr (*getArgSharding)(const Concept *impl, ::mlir::Operation *, unsigned);
    void (*setArgSharding)(const Concept *impl, ::mlir::Operation *, unsigned, mlir::sdy::TensorShardingAttr);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::sdy::ShardableRegionOpInterface;
    Model() : Concept{getArgSharding, setArgSharding} {}

    static inline mlir::sdy::TensorShardingAttr getArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index);
    static inline void setArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index, mlir::sdy::TensorShardingAttr sharding);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::sdy::ShardableRegionOpInterface;
    FallbackModel() : Concept{getArgSharding, setArgSharding} {}

    static inline mlir::sdy::TensorShardingAttr getArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index);
    static inline void setArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index, mlir::sdy::TensorShardingAttr sharding);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};
template <typename ConcreteOp>
struct ShardableRegionOpInterfaceTrait;

} // namespace detail
class ShardableRegionOpInterface : public ::mlir::OpInterface<ShardableRegionOpInterface, detail::ShardableRegionOpInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<ShardableRegionOpInterface, detail::ShardableRegionOpInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::ShardableRegionOpInterfaceTrait<ConcreteOp> {};
  /// Returns the sharding of the argument with the given index.
  mlir::sdy::TensorShardingAttr getArgSharding(unsigned index);
  /// Sets the shardings of the argument with the given index.
  void setArgSharding(unsigned index, mlir::sdy::TensorShardingAttr sharding);
};
namespace detail {
  template <typename ConcreteOp>
  struct ShardableRegionOpInterfaceTrait : public ::mlir::OpInterface<ShardableRegionOpInterface, detail::ShardableRegionOpInterfaceInterfaceTraits>::Trait<ConcreteOp> {
  };
}// namespace detail
} // namespace sdy
} // namespace mlir
namespace mlir {
namespace sdy {
template<typename ConcreteOp>
mlir::sdy::TensorShardingAttr detail::ShardableRegionOpInterfaceInterfaceTraits::Model<ConcreteOp>::getArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getArgSharding(index);
}
template<typename ConcreteOp>
void detail::ShardableRegionOpInterfaceInterfaceTraits::Model<ConcreteOp>::setArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index, mlir::sdy::TensorShardingAttr sharding) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).setArgSharding(index, sharding);
}
template<typename ConcreteOp>
mlir::sdy::TensorShardingAttr detail::ShardableRegionOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index) {
  return static_cast<const ConcreteOp *>(impl)->getArgSharding(tablegen_opaque_val, index);
}
template<typename ConcreteOp>
void detail::ShardableRegionOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::setArgSharding(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, unsigned index, mlir::sdy::TensorShardingAttr sharding) {
  return static_cast<const ConcreteOp *>(impl)->setArgSharding(tablegen_opaque_val, index, sharding);
}
} // namespace sdy
} // namespace mlir
