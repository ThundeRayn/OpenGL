#ifndef SPHERE_H
#define SPHERE_H

#include <memory>
#include "Vector3D.h"

using namespace std;
class Material;

class HitResult {
public:
    HitResult() { m_isHit = false; };
    bool m_isHit;
    Vector3D m_hitPos;
    Vector3D m_hitNormal;
    shared_ptr<Material> m_hitMaterial;
    float m_t;
};


class Sphere {
    
public:
    Sphere() {}
    Sphere(Vector3D center, float r, shared_ptr<Material> m)
    {
        m_center = center;
        m_radius = r;
        m_pMaterial = m;
    }
    HitResult hit(Ray& r, float min_t, float max_t);

    public:
    Vector3D m_center;
    float m_radius;
    shared_ptr<Material> m_pMaterial;
};


//test if ray hits this sphere within range min_t and max_t
HitResult Sphere::hit(Ray& ray, float min_t, float max_t)
{
    HitResult hit_result;
    //TODO: 2. compute ray hit information on the sphere
    //Answer: solve t and see if intersect
    Vector3D oc = operator-(ray.origin(),m_center);
    float half_b = dot(oc,ray.direction());
    float a = ray.direction().length_squared();
    float c = oc.length_squared()-m_radius*m_radius;
    float discriminant = half_b*half_b - a*c;
    //solve t
    float t = (-half_b-sqrt(discriminant))/a;
    if(discriminant>=0 && t>min_t && t<max_t){
        hit_result.m_isHit=true;
        hit_result.m_t=t;
        hit_result.m_hitPos = ray.at(t);
        hit_result.m_hitNormal = (operator-(hit_result.m_hitPos,m_center)*operator-(hit_result.m_hitPos,m_center))/m_radius;
        hit_result.m_hitMaterial = m_pMaterial;
    }else{
        hit_result.m_isHit=false;
    }
    /* and fill in hit result
    hit_result.m_isHit = ...;
    hit_result.m_t = ...;
    hit_result.m_hitPos = ...;
    hit_result.m_hitNormal = ...;
    hit_result.m_hitMaterial = ...;*/
    return hit_result;
}

#endif
