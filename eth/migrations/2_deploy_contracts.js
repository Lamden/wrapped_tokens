const ClearingHouse = artifacts.require("ClearingHouse");

module.exports = function(deployer) {
  deployer.deploy(ClearingHouse);
};
